# ✅ Checklist de Instalación y Verificación

## Pre-requisitos

- [ ] Python 3.10 o superior instalado
- [ ] MySQL 8.0 o superior instalado y corriendo
- [ ] Git instalado (opcional pero recomendado)
- [ ] Editor de código (VS Code, PyCharm, etc.)

## Paso 1: Verificar Instalaciones

```bash
# Verificar Python
python --version
# Debe mostrar: Python 3.10.x o superior

# Verificar pip
pip --version

# Verificar MySQL
mysql --version
```

- [ ] Python 3.10+ verificado
- [ ] pip verificado
- [ ] MySQL verificado

## Paso 2: Configurar Entorno Virtual

```bash
# Navegar al directorio del proyecto
cd c:\pruebas\ticketSystem

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate  # Windows
# El prompt debe cambiar mostrando (venv)
```

- [ ] Entorno virtual creado
- [ ] Entorno virtual activado (ver `(venv)` en el prompt)

## Paso 3: Instalar Dependencias

```bash
# Con el entorno virtual activado
pip install -r requirements.txt

# Verificar instalación
pip list
```

Verificar que se instalaron:
- [ ] Django 5.0.2
- [ ] djangorestframework
- [ ] mysqlclient
- [ ] python-decouple
- [ ] drf-yasg

## Paso 4: Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus credenciales
```

Editar el archivo `.env` y configurar:
- [ ] `SECRET_KEY` (generar una nueva para producción)
- [ ] `DEBUG=True`
- [ ] `DB_NAME=ticket_system`
- [ ] `DB_USER=root` (o tu usuario de MySQL)
- [ ] `DB_PASSWORD=` (tu contraseña de MySQL)
- [ ] `DB_HOST=localhost`
- [ ] `DB_PORT=3306`

## Paso 5: Crear Base de Datos MySQL

```bash
# Conectar a MySQL
mysql -u root -p
# Ingresar contraseña cuando se solicite
```

```sql
-- Ejecutar en MySQL
CREATE DATABASE ticket_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Verificar que se creó
SHOW DATABASES;
-- Debe aparecer 'ticket_system' en la lista

-- Salir de MySQL
EXIT;
```

- [ ] Base de datos `ticket_system` creada
- [ ] Charset utf8mb4 configurado

## Paso 6: Ejecutar Migraciones

```bash
# Crear archivos de migración
python manage.py makemigrations

# Debe mostrar:
# Migrations for 'usuarios':
#   apps/usuarios/migrations/0001_initial.py
# Migrations for 'tickets':
#   apps/tickets/migrations/0001_initial.py
# Migrations for 'reportes':
#   apps/reportes/migrations/0001_initial.py

# Aplicar migraciones a la base de datos
python manage.py migrate

# Debe mostrar:
# Running migrations:
#   Applying contenttypes.0001_initial... OK
#   Applying usuarios.0001_initial... OK
#   ...
```

- [ ] Migraciones creadas sin errores
- [ ] Migraciones aplicadas exitosamente
- [ ] No hay errores de conexión a MySQL

## Paso 7: Inicializar Datos Básicos

```bash
python manage.py init_data
```

Debe mostrar:
```
Inicializando datos básicos del sistema...
  Creando roles...
    ✓ Rol creado: Operativo (Nivel 1)
    ✓ Rol creado: Jefe de Área (Nivel 2)
    ✓ Rol creado: Supervisión General (Nivel 3)
  Creando áreas...
    ✓ Área creada: Soporte
    ✓ Área creada: Infraestructura
    ✓ Área creada: Por Definir
  Creando prioridades...
    ✓ Prioridad creada: Crítica (Nivel 1)
    ✓ Prioridad creada: Alta (Nivel 2)
    ✓ Prioridad creada: Media (Nivel 3)
    ✓ Prioridad creada: Baja (Nivel 4)
  Creando SLAs...
    ✓ SLA creado: SLA Crítico (...)
    ✓ SLA creado: SLA Alto (...)
    ✓ SLA creado: SLA Medio (...)
    ✓ SLA creado: SLA Bajo (...)
  Creando jornadas...
    ✓ Jornada creada: Matutina
    ✓ Jornada creada: Vespertina
    ✓ Jornada creada: Nocturna

✓ Datos básicos inicializados exitosamente
```

- [ ] 3 Roles creados
- [ ] 3 Áreas creadas
- [ ] 4 Prioridades creadas
- [ ] 4 SLAs creados
- [ ] 3 Jornadas creadas

## Paso 8: Crear Superusuario

```bash
python manage.py createsuperuser
```

Proporcionar:
```
Email: admin@example.com
Nombre: Administrador del Sistema
Password: ********
Password (again): ********
```

- [ ] Superusuario creado exitosamente
- [ ] Anotadas las credenciales de acceso

## Paso 9: Ejecutar Servidor de Desarrollo

```bash
python manage.py runserver
```

Debe mostrar:
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
March 10, 2026 - 12:00:00
Django version 5.0.2, using settings 'config.settings.development'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

- [ ] Servidor iniciado sin errores
- [ ] Mensaje "0 silenced issues" mostrado

## Paso 10: Verificar Acceso a Admin Panel

1. Abrir navegador
2. Ir a: http://localhost:8000/admin/
3. Iniciar sesión con credenciales del superusuario

Verificar que se puede acceder a:
- [ ] **Usuarios**: Ver modelo Usuario
- [ ] **Roles**: Ver modelo Rol
- [ ] **Tickets**: Ver modelo Ticket
- [ ] **Áreas**: Ver datos inicializados
- [ ] **Prioridades**: Ver datos inicializados
- [ ] **SLAs**: Ver datos inicializados
- [ ] **Jornadas**: Ver datos inicializados

## Paso 11: Verificar API Documentation

Abrir en navegador:

**Swagger UI**: http://localhost:8000/api/docs/
- [ ] Swagger UI accesible
- [ ] Se muestran endpoints de la API

**ReDoc**: http://localhost:8000/api/redoc/
- [ ] ReDoc accesible
- [ ] Documentación se visualiza correctamente

## Paso 12: Probar Funcionalidad Básica

### En Admin Panel:

1. **Crear un usuario operativo**:
   - [ ] Ir a Usuarios → Agregar usuario
   - [ ] Email: operativo1@test.com
   - [ ] Nombre: Operativo Prueba
   - [ ] Rol: Operativo (Nivel 1)
   - [ ] Password: test123
   - [ ] Guardar

2. **Crear un ticket manual**:
   - [ ] Ir a Tickets → Agregar ticket
   - [ ] Nombre: "Ticket de Prueba"
   - [ ] Estado: Abierto
   - [ ] Prioridad: Media
   - [ ] SLA: SLA Medio
   - [ ] Jornada: Matutina
   - [ ] Guardar

3. **Verificar el ticket**:
   - [ ] Ver que el ticket tiene un folio (ej: TKT-000001)
   - [ ] Ver el indicador de SLA (debe ser Verde 🟢)
   - [ ] Ver Historial de Estados (debe mostrar "Ticket creado")

### En Django Shell:

```bash
python manage.py shell_plus
```

```python
# Verificar usuarios
from apps.usuarios.models import Usuario, Rol
print(f"Total usuarios: {Usuario.objects.count()}")
print(f"Total roles: {Rol.objects.count()}")

# Verificar tickets
from apps.tickets.models import Ticket
print(f"Total tickets: {Ticket.objects.count()}")
print(f"Tickets abiertos: {Ticket.objects.abiertos().count()}")

# Ver primer ticket
ticket = Ticket.objects.first()
if ticket:
    print(f"Folio: {ticket.folio}")
    print(f"Estado SLA: {ticket.sla_status}")
    print(f"Puede cerrarse: {ticket.puede_cerrarse}")

# Probar servicio
from services.ticket_service import TicketService
from apps.tickets.models import Prioridad, SLA

datos = {
    'nombre': 'Ticket desde Shell',
    'descripcion': 'Probando el servicio',
    'prioridad_id': Prioridad.objects.first().id,
    'sla_id': SLA.objects.first().id,
}
nuevo_ticket = TicketService.crear_ticket(datos)
print(f"Ticket creado: {nuevo_ticket.folio}")
```

- [ ] Shell ejecutado sin errores
- [ ] Comandos ejecutados correctamente
- [ ] Ticket creado desde shell

## Paso 13: Verificar Logs

```bash
# Ver el archivo de logs
type logs\ticketSystem.log  # Windows CMD
Get-Content logs\ticketSystem.log  # PowerShell
cat logs/ticketSystem.log  # Linux/Mac
```

- [ ] Archivo de log existe
- [ ] Se registran operaciones

## 🎉 Instalación Completada

Si todos los checkboxes están marcados, la instalación es exitosa.

## ⚠️ Solución de Problemas Comunes

### Error: "No module named 'MySQLdb'"

```bash
pip install mysqlclient
# Si falla en Windows, instalar:
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient
```

### Error: "Access denied for user"

- Verificar credenciales en `.env`
- Verificar que MySQL está corriendo
- Verificar que el usuario tiene permisos

### Error: "Unknown database 'ticket_system'"

- Crear la base de datos manualmente:
```sql
CREATE DATABASE ticket_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Error: "Port 8000 is already in use"

```bash
# Usar otro puerto
python manage.py runserver 8080
```

### Error al ejecutar migraciones

```bash
# Limpiar y recrear migraciones
python manage.py migrate --fake-initial
```

## 📞 Siguiente Paso

Una vez completada la instalación, revisar:
- `docs/RESUMEN_PROYECTO.md` - Estado actual y próximos pasos
- `docs/DESARROLLO.md` - Guía de desarrollo
- `docs/ARQUITECTURA.md` - Diseño del sistema
- `docs/COMANDOS_RAPIDOS.md` - Comandos útiles

## 🚀 ¿Listo para Desarrollar?

El backend está completo. Los siguientes pasos son:
1. Implementar API REST (Serializers y ViewSets)
2. Crear autenticación JWT
3. Desarrollar frontend
4. Implementar testing

¡Feliz desarrollo! 🎊
