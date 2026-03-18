"""
Admin para Reportes y KPIs
"""
from django.contrib import admin
from .models import Reporte, KPI, SLAReporte


class KPIInline(admin.TabularInline):
    """Inline para KPIs"""
    model = KPI
    extra = 0
    readonly_fields = ['tiempo_promedio_atencion', 'tiempo_promedio_resolucion', 'cumplimiento_sla']
    can_delete = False


@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    """Admin para reportes"""
    list_display = ['tipo', 'area', 'fecha_generacion', 'generado_por_usuario']
    list_filter = ['tipo', 'area', 'fecha_generacion']
    search_fields = ['tipo']
    readonly_fields = ['fecha_generacion', 'generado_por_usuario']
    date_hierarchy = 'fecha_generacion'
    
    inlines = [KPIInline]


@admin.register(KPI)
class KPIAdmin(admin.ModelAdmin):
    """Admin para KPIs"""
    list_display = [
        'reporte', 'tiempo_promedio_atencion', 
        'tiempo_promedio_resolucion', 'cumplimiento_sla', 'created_at'
    ]
    list_filter = ['created_at']
    readonly_fields = ['reporte', 'tiempo_promedio_atencion', 'tiempo_promedio_resolucion', 'cumplimiento_sla']


@admin.register(SLAReporte)
class SLAReporteAdmin(admin.ModelAdmin):
    """Admin para reportes de SLA"""
    list_display = ['reporte', 'area', 'sla', 'prioridad', 'created_at']
    list_filter = ['area', 'sla', 'prioridad', 'created_at']
    readonly_fields = ['reporte', 'area', 'sla', 'prioridad']
