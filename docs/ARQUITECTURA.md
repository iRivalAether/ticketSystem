# Arquitectura del Sistema de Gestión de Tickets

## Información General

Este documento describe la arquitectura técnica del Sistema de Gestión de Procesos de Soporte (Ticketing).

## Stack Tecnológico

- **Backend Framework**: Django 5.0.2
- **Base de Datos**: MySQL 8.0+
- **API**: Django REST Framework 3.14.0
- **Lenguaje**: Python 3.10+
- **Patrón Arquitectónico**: MTV (Model-Template-View) con Service Layer

## Arquitectura en Capas

El sistema está organizado en las siguientes capas:

```
┌─────────────────────────────────────┐
│     Capa de Presentación            │ ← Templates / API REST
├─────────────────────────────────────┤
│     Capa de Controladores           │ ← Views / ViewSets
├─────────────────────────────────────┤
│     Capa de Servicios               │ ← Service Layer (Lógica de Negocio)
├─────────────────────────────────────┤
│     Capa de Datos (ORM)             │ ← Models / Managers
├─────────────────────────────────────┤
│     Base de Datos MySQL             │
└─────────────────────────────────────┘
```

### 1. Capa de Presentación

**Responsabilidad**: Interfaz con el usuario

**Componentes**:
- Templates Django (futuro)
- API REST con DRF
- Serializers (DTO Pattern)

### 2. Capa de Controladores

**Responsabilidad**: Manejo de requests HTTP

**Componentes**:
- Views (Function-based y Class-based)
- ViewSets (para API REST)
- Validación de entrada
- Formateo de respuestas

### 3. Capa de Servicios

**Responsabilidad**: Lógica de negocio centralizada

**Componentes**:
- `TicketService`: Operaciones de tickets
- `ReporteService`: Generación de reportes y KPIs

**Ventajas**:
- Reutilización de lógica
- Testing simplificado
- Separación de responsabilidades
- Transacciones atómicas

### 4. Capa de Datos

**Responsabilidad**: Acceso y persistencia de datos

**Componentes**:
- Models (ORM Django)
- Custom Managers (Repository Pattern)
- QuerySets especializados

## Patrones de Diseño Implementados

### 1. Service Layer Pattern

**Ubicación**: `services/`

**Propósito**: Centralizar la lógica de negocio

**Ejemplo**:
```python
from services.ticket_service import TicketService

ticket = TicketService.crear_ticket(datos, usuario)
```

**Beneficios**:
- Modelos más limpios
- Lógica reutilizable
- Transacciones atómicas
- Fácil testing

### 2. Repository Pattern

**Ubicación**: Custom Managers en `models.py`

**Propósito**: Abstraer el acceso a datos

**Ejemplo**:
```python
# Repository methods
tickets_abiertos = Ticket.objects.abiertos()
tickets_por_area = Ticket.objects.por_area(area)
usuarios_jefes = Usuario.objects.jefes_area()
```

**Beneficios**:
- Queries reutilizables
- Encapsulación de consultas complejas
- Código más legible

### 3. Factory Pattern

**Ubicación**: `UsuarioManager`

**Propósito**: Creación controlada de objetos

**Ejemplo**:
```python
# Factory methods
user = Usuario.objects.create_user(email, nombre, password)
superuser = Usuario.objects.create_superuser(email, nombre, password)
```

### 4. Strategy Pattern

**Ubicación**: Métodos de permisos en `Usuario`

**Propósito**: Comportamiento dinámico según rol

**Ejemplo**:
```python
# Estrategia basada en nivel jerárquico
tickets = TicketService.obtener_tickets_por_usuario(usuario)
# Retorna diferentes tickets según el nivel del usuario
```

### 5. Template Method Pattern

**Ubicación**: Modelos base en `apps.core.models`

**Propósito**: Definir estructura común para modelos

**Ejemplo**:
```python
class BaseModel(TimeStampedModel, SoftDeleteModel):
    # Define estructura común
    pass
```

### 6. Soft Delete Pattern

**Ubicación**: `SoftDeleteModel`

**Propósito**: Preservar datos históricos

**Ejemplo**:
```python
ticket.soft_delete()  # No elimina físicamente
ticket.restore()      # Recupera el registro
```

### 7. Command Pattern

**Ubicación**: Métodos de acciones en `Ticket`

**Propósito**: Encapsular operaciones como objetos

**Ejemplo**:
```python
ticket.asignar_a(usuario, asignado_por, motivo)
ticket.iniciar_atencion(usuario, comentario)
ticket.cerrar(usuario, comentario)
```

### 8. Facade Pattern

**Ubicación**: `TicketService`

**Propósito**: Simplificar interfaces complejas

**Ejemplo**:
```python
# Facade que coordina múltiples operaciones
TicketService.realizar_triaje(ticket_id, area_id, prioridad_id, jefe)
```

## Aplicaciones Django

### apps.core

**Propósito**: Funcionalidad común del sistema

**Componentes**:
- `BaseModel`: Modelo base con timestamps y soft delete
- Utilidades compartidas

### apps.usuarios

**Propósito**: Gestión de usuarios y roles

**Componentes**:
- `Usuario`: Modelo de usuario personalizado
- `Rol`: Jerarquía de 3 niveles
- Autenticación por email

**Jerarquía**:
1. **Nivel 1 - Operativos**: Solo ven tickets asignados
2. **Nivel 2 - Jefes de Área**: Triaje y asignación
3. **Nivel 3 - Supervisión General**: Visión global

### apps.tickets

**Propósito**: Sistema central de tickets

**Componentes**:
- `Ticket`: Modelo principal con SLA y FIFO
- `TicketEstadoHistorial`: Trazabilidad de estados
- `TicketAsignacionHistorial`: Auditoría de asignaciones
- `Area`, `Prioridad`, `SLA`, `Jornada`: Entidades de soporte

**Estados del Ticket**:
1. Abierto
2. Asignado
3. En Atención
4. Cerrado
5. Cerrado Automático

### apps.reportes

**Propósito**: Generación de reportes y KPIs

**Componentes**:
- `Reporte`: Reportes semanales/mensuales
- `KPI`: Métricas de rendimiento
- `SLAReporte`: Análisis de SLA

## Flujo de Trabajo del Sistema

### 1. Creación de Ticket

```
Usuario → TicketService.crear_ticket()
         → Ticket.objects.create()
         → Signal post_save
         → TicketEstadoHistorial (registrar estado inicial)
```

### 2. Triaje (Jefe de Área)

```
Jefe → TicketService.realizar_triaje()
     → Validar permisos
     → Actualizar área y prioridad
     → Registrar en historial
```

### 3. Asignación

```
Jefe → TicketService.asignar_ticket()
     → Validar permisos
     → ticket.asignar_a()
     → TicketAsignacionHistorial.create()
     → TicketEstadoHistorial.create()
```

### 4. Atención

```
Operativo → TicketService.iniciar_atencion_ticket()
          → Validar asignación
          → ticket.iniciar_atencion()
          → Registrar timestamp de inicio
```

### 5. Cierre

```
Usuario → TicketService.cerrar_ticket()
        → Validar permisos
        → ticket.cerrar()
        → Registrar fecha de cierre
        → TicketEstadoHistorial.create()
```

## Control de SLA

### Semáforo de Estados

**Verde** 🟢: Dentro de tiempo (< 80% del SLA)
**Amarillo** 🟡: Próximo a vencer (80-100% del SLA)
**Rojo** 🔴: SLA vencido (> 100% del SLA)

### Cálculo Dinámico

```python
@property
def sla_status(self):
    tiempo_restante = self.tiempo_limite_resolucion - timezone.now()
    porcentaje_usado = ((tiempo_total - tiempo_restante) / tiempo_total) * 100
    
    if porcentaje_usado >= 100:
        return 'rojo'
    elif porcentaje_usado >= 80:
        return 'amarillo'
    else:
        return 'verde'
```

## Principio FIFO

Los tickets se atienden en orden de llegada:

```python
class Ticket(BaseModel):
    class Meta:
        ordering = ['fecha_creacion']  # FIFO: First In, First Out
```

## Seguridad

### Validación de Permisos por Nivel

```python
def puede_ver_ticket(self, ticket):
    if self.es_supervision_general:
        return True
    if self.es_jefe_area:
        return ticket.area == self.get_area()
    if self.es_operativo:
        return ticket.asignado_a == self
    return False
```

### Transacciones Atómicas

```python
@transaction.atomic
def crear_ticket(datos, usuario):
    # Todas las operaciones se ejecutan o ninguna
    ticket = Ticket.objects.create(...)
    historial = TicketEstadoHistorial.objects.create(...)
    return ticket
```

## Logging

Sistema de logging configurado en múltiples niveles:

```python
LOGGING = {
    'loggers': {
        'apps': {'level': 'DEBUG'},
        'services': {'level': 'DEBUG'},
        'django': {'level': 'INFO'},
    }
}
```

## Configuración por Ambiente

- `config/settings/base.py`: Configuración común
- `config/settings/development.py`: Desarrollo
- `config/settings/production.py`: Producción

## Management Commands

### Inicializar datos

```bash
python manage.py init_data
```

### Cerrar tickets inactivos

```bash
python manage.py cerrar_tickets_inactivos
```

## Próximos Pasos

1. Implementar Views y ViewSets para API REST
2. Crear Serializers para DTOs
3. Implementar autenticación JWT
4. Desarrollo de frontend
5. Testing unitario y de integración
6. Documentación de API con Swagger

## Diagrama de Componentes

```
ticketSystem/
├── apps/
│   ├── core/           # Funcionalidad común
│   ├── usuarios/       # Gestión de usuarios
│   ├── tickets/        # Sistema de tickets
│   └── reportes/       # Reportes y KPIs
├── services/           # Capa de servicios
│   ├── ticket_service.py
│   └── reporte_service.py
├── config/             # Configuración
│   ├── settings/
│   ├── urls.py
│   └── wsgi.py
└── manage.py
```
