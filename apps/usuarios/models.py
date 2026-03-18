"""
Modelos de Usuario y Rol

Estructura jerárquica de 3 niveles:
- Nivel 1: Operativos (trabajadores normales)
- Nivel 2: Jefes de Área
- Nivel 3: Supervisión General / Administración
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from apps.core.models import BaseModel


class RolManager(models.Manager):
    """
    Manager personalizado para Rol
    Pattern: Repository Pattern
    """
    def operativos(self):
        """Retorna roles de nivel operativo"""
        return self.filter(nivel_jerarquico=1, is_active=True)
    
    def jefes_area(self):
        """Retorna roles de jefes de área"""
        return self.filter(nivel_jerarquico=2, is_active=True)
    
    def supervision_general(self):
        """Retorna roles de supervisión general"""
        return self.filter(nivel_jerarquico=3, is_active=True)


class Rol(BaseModel):
    """
    Modelo de Rol con jerarquía de 3 niveles
    Basado en tabla 'rol' del diagrama
    """
    NIVEL_OPERATIVO = 1
    NIVEL_JEFE_AREA = 2
    NIVEL_SUPERVISION_GENERAL = 3
    
    NIVELES_JERARQUICOS = [
        (NIVEL_OPERATIVO, 'Operativo'),
        (NIVEL_JEFE_AREA, 'Jefe de Área'),
        (NIVEL_SUPERVISION_GENERAL, 'Supervisión General'),
    ]
    
    nombre = models.CharField(
        'Nombre del rol',
        max_length=50,
        unique=True
    )
    nivel_jerarquico = models.IntegerField(
        'Nivel jerárquico',
        choices=NIVELES_JERARQUICOS,
        default=NIVEL_OPERATIVO,
        db_index=True,
        help_text='Nivel 1: Operativos, Nivel 2: Jefes de Área, Nivel 3: Supervisión General'
    )
    
    objects = RolManager()
    
    class Meta:
        db_table = 'rol'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        ordering = ['nivel_jerarquico', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} (Nivel {self.nivel_jerarquico})"
    
    @property
    def es_operativo(self):
        """Verifica si es rol operativo (Nivel 1)"""
        return self.nivel_jerarquico == self.NIVEL_OPERATIVO
    
    @property
    def es_jefe_area(self):
        """Verifica si es jefe de área (Nivel 2)"""
        return self.nivel_jerarquico == self.NIVEL_JEFE_AREA
    
    @property
    def es_supervision_general(self):
        """Verifica si es supervisión general (Nivel 3)"""
        return self.nivel_jerarquico == self.NIVEL_SUPERVISION_GENERAL


class UsuarioManager(BaseUserManager):
    """
    Manager personalizado para el modelo Usuario
    Pattern: Factory Pattern
    """
    def create_user(self, email, nombre, password=None, **extra_fields):
        """Crea y guarda un usuario regular"""
        if not email:
            raise ValueError('El usuario debe tener un email')
        
        email = self.normalize_email(email)
        user = self.model(email=email, nombre=nombre, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, nombre, password=None, **extra_fields):
        """Crea y guarda un superusuario"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, nombre, password, **extra_fields)
    
    def operativos(self):
        """Retorna usuarios operativos (nivel 1)"""
        return self.filter(rol__nivel_jerarquico=1, is_active=True)
    
    def jefes_area(self):
        """Retorna jefes de área (nivel 2)"""
        return self.filter(rol__nivel_jerarquico=2, is_active=True)
    
    def supervision_general(self):
        """Retorna supervisión general (nivel 3)"""
        return self.filter(rol__nivel_jerarquico=3, is_active=True)


class Usuario(AbstractBaseUser, PermissionsMixin, BaseModel):
    """
    Modelo de Usuario personalizado
    Basado en tabla 'usuario' del diagrama
    
    Implementa autenticación por email en lugar de username
    """
    nombre = models.CharField(
        'Nombre completo',
        max_length=150
    )
    email = models.EmailField(
        'Email',
        max_length=190,
        unique=True,
        db_index=True
    )
    rol = models.ForeignKey(
        Rol,
        on_delete=models.PROTECT,
        related_name='usuarios',
        verbose_name='Rol'
    )
    area = models.ForeignKey(
        'tickets.Area',
        on_delete=models.SET_NULL,
        related_name='usuarios',
        verbose_name='Área',
        null=True,
        blank=True,
        help_text='Área a la que pertenece el usuario (requerido para operativos y jefes)'
    )
    is_staff = models.BooleanField(
        'Staff',
        default=False,
        help_text='Determina si el usuario puede acceder al admin'
    )
    
    objects = UsuarioManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']
    
    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.email})"
    
    @property
    def nivel_jerarquico(self):
        """Retorna el nivel jerárquico del usuario"""
        return self.rol.nivel_jerarquico if self.rol else None
    
    @property
    def es_operativo(self):
        """Verifica si es usuario operativo (Nivel 1)"""
        return self.rol.es_operativo if self.rol else False
    
    @property
    def es_jefe_area(self):
        """Verifica si es jefe de área (Nivel 2)"""
        return self.rol.es_jefe_area if self.rol else False
    
    @property
    def es_supervision_general(self):
        """Verifica si es supervisión general (Nivel 3)"""
        return self.rol.es_supervision_general if self.rol else False
    
    def puede_ver_ticket(self, ticket):
        """
        Determina si el usuario puede ver un ticket específico
        Pattern: Strategy Pattern
        """
        # Nivel 3: ve todos los tickets
        if self.es_supervision_general:
            return True
        
        # Nivel 2: ve tickets de su área
        if self.es_jefe_area:
            return ticket.area == self.get_area()
        
        # Nivel 1: solo tickets asignados a él
        if self.es_operativo:
            return ticket.usuario_asignado == self
        
        return False
    
    def puede_asignar_ticket(self):
        """Determina si el usuario puede asignar tickets"""
        return self.es_jefe_area or self.es_supervision_general
    
    def puede_ver_reportes_globales(self):
        """Determina si puede ver reportes globales"""
        return self.es_supervision_general
    
    def get_area(self):
        """Retorna el área del usuario"""
        return self.area
