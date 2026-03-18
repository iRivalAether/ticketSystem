"""
Admin para Tickets
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Ticket, TicketEstadoHistorial, TicketAsignacionHistorial,
    Area, Prioridad, SLA, Jornada, SemaforoSLAConfig
)


class TicketEstadoHistorialInline(admin.TabularInline):
    """Inline para historial de estados"""
    model = TicketEstadoHistorial
    extra = 0
    readonly_fields = ['estado', 'fecha', 'usuario', 'comentario']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


class TicketAsignacionHistorialInline(admin.TabularInline):
    """Inline para historial de asignaciones"""
    model = TicketAsignacionHistorial
    extra = 0
    readonly_fields = ['asignado_a_usuario', 'asignado_por_usuario', 'fecha_asignacion', 'motivo']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """Admin para el modelo Ticket"""
    list_display = [
        'folio_display', 'nombre', 'estado', 'sla_indicator', 
        'area', 'usuario_asignado', 'prioridad', 'jornada', 'fecha_creacion'
    ]
    list_filter = ['estado', 'area', 'prioridad', 'jornada', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion', 'pk']
    readonly_fields = ['folio', 'fecha_creacion', 'fecha_cierre', 'tiempo_transcurrido', 'sla_status_display']
    date_hierarchy = 'fecha_creacion'
    
    fieldsets = (
        ('Información del Ticket', {
            'fields': ('folio', 'nombre', 'descripcion', 'estado')
        }),
        ('Clasificación', {
            'fields': ('area', 'prioridad', 'jornada')
        }),
        ('Asignación', {
            'fields': ('usuario_asignado',)
        }),
        ('SLA y Tiempos', {
            'fields': ('sla', 'sla_status_display', 'fecha_creacion', 'fecha_inicio_atencion', 'fecha_cierre', 'tiempo_transcurrido')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
    )
    
    inlines = [TicketEstadoHistorialInline, TicketAsignacionHistorialInline]
    
    def folio_display(self, obj):
        """Muestra el folio del ticket"""
        return obj.folio
    folio_display.short_description = 'Folio'
    folio_display.admin_order_field = 'pk'
    
    def sla_indicator(self, obj):
        """Muestra un indicador visual del estado del SLA"""
        colors = {
            'verde': '#28a745',
            'amarillo': '#ffc107',
            'rojo': '#dc3545',
        }
        status = obj.sla_status
        color = colors.get(status, '#6c757d')
        return format_html(
            '<span style="display: inline-block; width: 15px; height: 15px; '
            'background-color: {}; border-radius: 50%;"></span>',
            color
        )
    sla_indicator.short_description = 'SLA'
    
    def sla_status_display(self, obj):
        """Muestra el estado del SLA con texto y color"""
        colors = {
            'verde': '#28a745',
            'amarillo': '#ffc107',
            'rojo': '#dc3545',
        }
        status = obj.sla_status
        color = colors.get(status, '#6c757d')
        labels = {
            'verde': 'Dentro de tiempo',
            'amarillo': 'Próximo a vencer',
            'rojo': 'SLA vencido',
        }
        return format_html(
            '<span style="padding: 5px 10px; background-color: {}; color: white; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color, labels.get(status, 'Desconocido')
        )
    sla_status_display.short_description = 'Estado SLA'


@admin.register(TicketEstadoHistorial)
class TicketEstadoHistorialAdmin(admin.ModelAdmin):
    """Admin para historial de estados"""
    list_display = ['ticket', 'estado', 'fecha', 'usuario', 'comentario']
    list_filter = ['estado', 'fecha']
    search_fields = ['ticket__nombre', 'comentario']
    readonly_fields = ['ticket', 'estado', 'fecha', 'usuario', 'comentario']
    date_hierarchy = 'fecha'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TicketAsignacionHistorial)
class TicketAsignacionHistorialAdmin(admin.ModelAdmin):
    """Admin para historial de asignaciones"""
    list_display = ['ticket', 'asignado_a_usuario', 'asignado_por_usuario', 'fecha_asignacion', 'motivo']
    list_filter = ['fecha_asignacion']
    search_fields = ['ticket__nombre', 'asignado_a_usuario__nombre', 'motivo']
    readonly_fields = ['ticket', 'asignado_a_usuario', 'asignado_por_usuario', 'fecha_asignacion', 'motivo']
    date_hierarchy = 'fecha_asignacion'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    """Admin para áreas"""
    list_display = ['nombre', 'is_active', 'created_at']
    search_fields = ['nombre']
    list_filter = ['is_active']


@admin.register(Prioridad)
class PrioridadAdmin(admin.ModelAdmin):
    """Admin para prioridades"""
    list_display = ['nombre', 'nivel', 'is_active', 'created_at']
    search_fields = ['nombre']
    list_filter = ['nivel', 'is_active']
    ordering = ['nivel']


@admin.register(SLA)
class SLAAdmin(admin.ModelAdmin):
    """Admin para SLAs"""
    list_display = ['nombre', 'tiempo_respuesta', 'tiempo_resolucion', 'is_active', 'created_at']
    search_fields = ['nombre']
    list_filter = ['is_active']


@admin.register(Jornada)
class JornadaAdmin(admin.ModelAdmin):
    """Admin para jornadas"""
    list_display = ['nombre', 'is_active', 'created_at']
    search_fields = ['nombre']
    list_filter = ['is_active']


@admin.register(SemaforoSLAConfig)
class SemaforoSLAConfigAdmin(admin.ModelAdmin):
    """Admin para configuración de umbrales de semáforo SLA"""
    list_display = ['nombre', 'warning_percentage', 'danger_percentage', 'is_active', 'updated_at']
    list_filter = ['is_active']
    search_fields = ['nombre']
