# Guía de Vistas Web - Sistema de Tickets

## Esquema de Colores

El sistema utiliza un esquema de colores profesional y elegante:

- **Blanco (#FFFFFF)**: Fondos principales, backgrounds de cards
- **Negro (#1a1a1a)**: Texto, estructura, bordes, iconos
- **Dorado (#D4AF37)**: Elementos destacados, botones, indicadores activos

## Templates Creados

### 1. Base Template
- **Archivo**: `templates/base.html`
- **Función**: Template base con navbar, footer y estructura común
- **Elementos**:
  - Navbar con navegación condicional por rol
  - Sistema de mensajes flash
  - Footer con información del sistema
  - Carga de CSS personalizado

### 2. Login
- **Archivo**: `templates/registration/login.html`
- **Función**: Pantalla de inicio de sesión
- **Características**:
  - Diseño elegante con gradiente negro
  - Logo dorado destacado
  - Formulario limpio y profesional

### 3. Dashboard
- **Archivo**: `templates/dashboard.html`
- **Función**: Vista principal del usuario
- **Componentes**:
  - KPIs en cards (Tickets abiertos, en atención, SLA crítico, cumplimiento)
  - Próximo ticket FIFO (solo para operativos)
  - Tabla de tickets activos
  - Tickets pendientes de triaje (solo para jefes de área)
  - Estadísticas por jornada (solo para supervisión general)

### 4. Lista de Tickets
- **Archivo**: `templates/tickets/ticket_list.html`
- **Función**: Listado completo de tickets con filtros
- **Características**:
  - Filtros por estado, área, prioridad, SLA
  - Tabla con paginación
  - Indicadores visuales de SLA (semáforo verde/amarillo/rojo)
  - Botón para crear nuevos tickets

### 5. Detalle de Ticket
- **Archivo**: `templates/tickets/ticket_detail.html`
- **Función**: Vista detallada de un ticket específico
- **Secciones**:
  - Información completa del ticket (2 columnas)
  - Historial de estados con timeline visual
  - Panel lateral con control de SLA
  - Fechas clave (creación, asignación, inicio, cierre)
  - Botones de acción según estado y usuario

### 6. Crear Ticket
- **Archivo**: `templates/tickets/ticket_form.html`
- **Función**: Formulario para crear nuevos tickets
- **Campos**:
  - Título
  - Descripción (textarea)
  - Prioridad (select)

### 7. Cerrar Ticket
- **Archivo**: `templates/tickets/ticket_cerrar.html`
- **Función**: Formulario para cerrar un ticket
- **Campos**:
  - Solución aplicada (textarea obligatorio)
  - Comentarios adicionales (textarea opcional)

### 8. Lista de Triaje
- **Archivo**: `templates/tickets/ticket_triaje_list.html`
- **Función**: Tickets pendientes de asignación (Jefes de Área)
- **Características**:
  - Tabla de tickets sin área asignada
  - Indicadores de SLA urgentes
  - Botón para realizar triaje

### 9. Realizar Triaje
- **Archivo**: `templates/tickets/ticket_triaje_form.html`
- **Función**: Asignar área y usuario a un ticket
- **Layout**: 2 columnas (información del ticket + formulario de asignación)
- **Campos**:
  - Área (select obligatorio)
  - Usuario asignado (select opcional)
  - Comentarios (textarea opcional)

### 10. Reportes
- **Archivo**: `templates/reportes/dashboard.html`
- **Función**: Dashboard de estadísticas globales (Supervisión General)
- **Componentes**:
  - Estadísticas de SLA (verde/amarillo/rojo)
  - Porcentaje de cumplimiento general

## Formularios (Forms)

### TicketCreateForm
- **Archivo**: `apps/tickets/forms.py`
- **Uso**: Crear tickets (Nivel 1 - Operativos)
- **Campos**: titulo, descripcion, prioridad

### TicketTriajeForm
- **Archivo**: `apps/tickets/forms.py`
- **Uso**: Realizar triaje (Nivel 2 - Jefes de Área)
- **Campos**: area, usuario_asignado, comentario
- **Lógica**: Carga dinámicamente usuarios del área del jefe

### TicketCerrarForm
- **Archivo**: `apps/tickets/forms.py`
- **Uso**: Cerrar tickets
- **Campos**: solucion (obligatorio), comentario (opcional)

## Vistas (Views)

Todas las vistas están en `apps/tickets/views.py`:

1. **dashboard**: Vista principal con KPIs y próximo ticket FIFO
2. **ticket_list**: Listado de tickets con filtros y paginación
3. **ticket_detail**: Detalle completo de un ticket con historial
4. **ticket_crear**: Crear nuevo ticket usando TicketService
5. **ticket_triaje**: Lista de tickets pendientes de triaje
6. **ticket_realizar_triaje**: Asignar área y usuario a ticket
7. **ticket_atencion**: Iniciar atención (cambia estado a EN_ATENCION)
8. **ticket_cerrar**: Cerrar ticket con solución
9. **reportes**: Dashboard de reportes globales

## URLs

Todas las URLs están configuradas en `config/urls.py`:

```
/                                    → dashboard
/login/                              → login
/logout/                             → logout
/tickets/                            → ticket_list
/tickets/crear/                      → ticket_crear
/tickets/<id>/                       → ticket_detail
/tickets/<id>/atencion/              → ticket_atencion
/tickets/<id>/cerrar/                → ticket_cerrar
/triaje/                             → ticket_triaje
/triaje/<id>/                        → ticket_realizar_triaje
/reportes/                           → reportes
```

## Características de Seguridad

- ✅ Todas las vistas requieren autenticación (`@login_required`)
- ✅ Validación de permisos basada en roles (puede_ver_ticket, puede_asignar_ticket, puede_ver_reportes_globales)
- ✅ Uso de CSRF tokens en todos los formularios
- ✅ Mensajes flash para feedback al usuario
- ✅ Redirects seguros

## Navegación Jerárquica

### Nivel 1 - Operativo
- Dashboard con próximo ticket FIFO
- Ver sus tickets asignados
- Crear tickets
- Iniciar atención
- Cerrar tickets propios

### Nivel 2 - Jefe de Área
- Todo lo de Nivel 1
- Ver tickets de su área
- Realizar triaje
- Asignar tickets a operativos

### Nivel 3 - Supervisión General
- Todo lo de Nivel 2
- Ver todos los tickets del sistema
- Acceso a reportes globales
- Estadísticas por jornada y área

## Elementos Visuales

### Indicadores SLA
- **Verde**: < 80% del tiempo límite
- **Amarillo**: 80-100% del tiempo límite
- **Rojo**: > 100% del tiempo límite (vencido)

### Badges de Estado
- **Abierto**: badge-warning (amarillo)
- **Asignado**: badge-secondary (gris)
- **En Atención**: badge-dorado (dorado)
- **Cerrado**: badge-success (verde)

### Cards y Layout
- Cards con borde negro y hover effect
- Grid responsivo para estadísticas
- Tablas con zebra striping
- Botones dorados para acciones principales
- Botones negros para acciones secundarias

## Responsive Design

- Grid adaptable con `grid-template-columns: repeat(auto-fit, minmax(250px, 1fr))`
- Media queries para pantallas < 768px
- Navegación colapsable en mobile
- Tablas con scroll horizontal en pantallas pequeñas
