"""
Comando para inicializar datos básicos del sistema

Uso:
    python manage.py init_data
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.usuarios.models import Rol, Usuario
from apps.tickets.models import Area, Prioridad, SLA, Jornada


class Command(BaseCommand):
    help = 'Inicializa datos básicos del sistema (Roles, Áreas, Prioridades, SLAs, Jornadas)'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Inicializando datos básicos del sistema...')
        
        # Crear Roles
        self.stdout.write('  Creando roles...')
        roles_data = [
            {'nombre': 'Operativo', 'nivel_jerarquico': Rol.NIVEL_OPERATIVO},
            {'nombre': 'Jefe de Área', 'nivel_jerarquico': Rol.NIVEL_JEFE_AREA},
            {'nombre': 'Supervisión General', 'nivel_jerarquico': Rol.NIVEL_SUPERVISION_GENERAL},
        ]
        
        for rol_data in roles_data:
            rol, created = Rol.objects.get_or_create(**rol_data)
            if created:
                self.stdout.write(self.style.SUCCESS(f'    ✓ Rol creado: {rol}'))
            else:
                self.stdout.write(f'    - Rol ya existe: {rol}')
        
        # Crear Áreas
        self.stdout.write('  Creando áreas...')
        areas_data = ['Soporte', 'Infraestructura', 'Por Definir']
        
        for area_nombre in areas_data:
            area, created = Area.objects.get_or_create(nombre=area_nombre)
            if created:
                self.stdout.write(self.style.SUCCESS(f'    ✓ Área creada: {area}'))
            else:
                self.stdout.write(f'    - Área ya existe: {area}')
        
        # Crear Prioridades
        self.stdout.write('  Creando prioridades...')
        prioridades_data = [
            {'nombre': 'Crítica', 'nivel': 1},
            {'nombre': 'Alta', 'nivel': 2},
            {'nombre': 'Media', 'nivel': 3},
            {'nombre': 'Baja', 'nivel': 4},
        ]
        
        for prioridad_data in prioridades_data:
            prioridad, created = Prioridad.objects.get_or_create(**prioridad_data)
            if created:
                self.stdout.write(self.style.SUCCESS(f'    ✓ Prioridad creada: {prioridad}'))
            else:
                self.stdout.write(f'    - Prioridad ya existe: {prioridad}')
        
        # Crear SLAs
        self.stdout.write('  Creando SLAs...')
        slas_data = [
            {'nombre': 'SLA Crítico', 'tiempo_respuesta': 15, 'tiempo_resolucion': 4},
            {'nombre': 'SLA Alto', 'tiempo_respuesta': 30, 'tiempo_resolucion': 8},
            {'nombre': 'SLA Medio', 'tiempo_respuesta': 60, 'tiempo_resolucion': 24},
            {'nombre': 'SLA Bajo', 'tiempo_respuesta': 120, 'tiempo_resolucion': 48},
        ]
        
        for sla_data in slas_data:
            sla, created = SLA.objects.get_or_create(**sla_data)
            if created:
                self.stdout.write(self.style.SUCCESS(f'    ✓ SLA creado: {sla}'))
            else:
                self.stdout.write(f'    - SLA ya existe: {sla}')
        
        # Crear Jornadas
        self.stdout.write('  Creando jornadas...')
        jornadas_data = [
            Jornada.MATUTINA,
            Jornada.VESPERTINA,
            Jornada.NOCTURNA,
        ]
        
        for jornada_nombre in jornadas_data:
            jornada, created = Jornada.objects.get_or_create(nombre=jornada_nombre)
            if created:
                self.stdout.write(self.style.SUCCESS(f'    ✓ Jornada creada: {jornada}'))
            else:
                self.stdout.write(f'    - Jornada ya existe: {jornada}')

        # Crear usuarios demo por área
        self.stdout.write('  Creando usuarios demo...')
        rol_operativo = Rol.objects.get(nivel_jerarquico=Rol.NIVEL_OPERATIVO)
        rol_jefe = Rol.objects.get(nivel_jerarquico=Rol.NIVEL_JEFE_AREA)
        rol_supervisor = Rol.objects.get(nivel_jerarquico=Rol.NIVEL_SUPERVISION_GENERAL)
        area_soporte = Area.objects.get(nombre='Soporte')
        area_infra = Area.objects.get(nombre='Infraestructura')

        usuarios_demo = [
            {
                'email': 'operativo.soporte@test.com',
                'nombre': 'Operativo Soporte',
                'rol': rol_operativo,
                'area': area_soporte,
                'is_staff': False,
                'is_superuser': False,
            },
            {
                'email': 'operativo.infra@test.com',
                'nombre': 'Operativo Infraestructura',
                'rol': rol_operativo,
                'area': area_infra,
                'is_staff': False,
                'is_superuser': False,
            },
            {
                'email': 'jefe.soporte@test.com',
                'nombre': 'Jefe Soporte',
                'rol': rol_jefe,
                'area': area_soporte,
                'is_staff': True,
                'is_superuser': False,
            },
            {
                'email': 'supervisor@test.com',
                'nombre': 'Supervisor General',
                'rol': rol_supervisor,
                'area': None,
                'is_staff': True,
                'is_superuser': True,
            },
        ]

        for user_data in usuarios_demo:
            user, created = Usuario.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    'nombre': user_data['nombre'],
                    'rol': user_data['rol'],
                    'area': user_data['area'],
                    'is_staff': user_data['is_staff'],
                    'is_superuser': user_data['is_superuser'],
                }
            )

            if created:
                user.set_password('demo123')
                user.save(update_fields=['password'])
                self.stdout.write(self.style.SUCCESS(f"    ✓ Usuario creado: {user.email} / demo123"))
            else:
                user.nombre = user_data['nombre']
                user.rol = user_data['rol']
                user.area = user_data['area']
                user.is_staff = user_data['is_staff']
                user.is_superuser = user_data['is_superuser']
                user.is_active = True
                user.save()
                self.stdout.write(f"    - Usuario actualizado: {user.email}")
        
        self.stdout.write(self.style.SUCCESS('\n✓ Datos básicos inicializados exitosamente'))
