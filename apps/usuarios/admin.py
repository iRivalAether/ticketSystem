"""
Admin para Usuarios y Roles
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario, Rol


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    """Admin para el modelo Rol"""
    list_display = ['nombre', 'nivel_jerarquico', 'get_nivel_display', 'is_active', 'created_at']
    list_filter = ['nivel_jerarquico', 'is_active']
    search_fields = ['nombre']
    ordering = ['nivel_jerarquico', 'nombre']
    
    fieldsets = (
        ('Información del Rol', {
            'fields': ('nombre', 'nivel_jerarquico')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
    )
    
    def get_nivel_display(self, obj):
        """Muestra el nivel jerárquico en texto"""
        return dict(Rol.NIVELES_JERARQUICOS).get(obj.nivel_jerarquico)
    get_nivel_display.short_description = 'Nivel'


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    """Admin para el modelo Usuario"""
    list_display = ['email', 'nombre', 'rol', 'nivel_jerarquico', 'is_active', 'is_staff']
    list_filter = ['rol__nivel_jerarquico', 'is_active', 'is_staff', 'rol']
    search_fields = ['email', 'nombre']
    ordering = ['nombre']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('email', 'nombre', 'password')
        }),
        ('Rol y Permisos', {
            'fields': ('rol', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Fechas Importantes', {
            'fields': ('last_login', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('Crear Usuario', {
            'classes': ('wide',),
            'fields': ('email', 'nombre', 'rol', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_login']
    filter_horizontal = ('groups', 'user_permissions')
