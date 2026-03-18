"""
Modelos de Reportes y KPIs

Basado en las tablas del diagrama:
- reporte
- kpi
- sla_reporte
"""
from django.db import models
from django.conf import settings
from apps.core.models import BaseModel


class Reporte(BaseModel):
    """
    Modelo de Reporte
    Basado en tabla 'reporte' del diagrama
    """
    TIPO_SEMANAL = 'semanal'
    TIPO_MENSUAL = 'mensual'
    TIPO_PERSONALIZADO = 'personalizado'
    
    TIPOS_REPORTE = [
        (TIPO_SEMANAL, 'Reporte Semanal'),
        (TIPO_MENSUAL, 'Reporte Mensual'),
        (TIPO_PERSONALIZADO, 'Reporte Personalizado'),
    ]
    
    tipo = models.CharField(
        'Tipo de reporte',
        max_length=80,
        choices=TIPOS_REPORTE
    )
    fecha_generacion = models.DateTimeField(
        'Fecha de generación',
        auto_now_add=True,
        db_index=True
    )
    generado_por_usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='reportes_generados',
        verbose_name='Generado por',
        null=True,
        blank=True
    )
    area = models.ForeignKey(
        'tickets.Area',
        on_delete=models.SET_NULL,
        related_name='reportes',
        verbose_name='Área',
        null=True,
        blank=True,
        help_text='Si está vacío, es un reporte global'
    )
    
    class Meta:
        db_table = 'reporte'
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'
        ordering = ['-fecha_generacion']
        indexes = [
            models.Index(fields=['-fecha_generacion', 'tipo']),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.fecha_generacion.strftime('%Y-%m-%d')}"


class KPI(BaseModel):
    """
    Modelo de KPI (Key Performance Indicator)
    Basado en tabla 'kpi' del diagrama
    
    Almacena métricas de rendimiento del sistema
    """
    reporte = models.ForeignKey(
        Reporte,
        on_delete=models.CASCADE,
        related_name='kpis',
        verbose_name='Reporte'
    )
    tiempo_promedio_atencion = models.FloatField(
        'Tiempo promedio de atención (minutos)',
        null=True,
        blank=True
    )
    tiempo_promedio_resolucion = models.FloatField(
        'Tiempo promedio de resolución (horas)',
        null=True,
        blank=True
    )
    cumplimiento_sla = models.FloatField(
        'Cumplimiento de SLA (%)',
        null=True,
        blank=True,
        help_text='Porcentaje de tickets que cumplieron el SLA'
    )
    
    class Meta:
        db_table = 'kpi'
        verbose_name = 'KPI'
        verbose_name_plural = 'KPIs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"KPI - {self.reporte}"


class SLAReporte(BaseModel):
    """
    Modelo de Reporte de SLA
    Basado en tabla 'sla_reporte' del diagrama (si existe)
    
    Almacena métricas específicas de cumplimiento de SLA
    """
    reporte = models.ForeignKey(
        Reporte,
        on_delete=models.CASCADE,
        related_name='sla_reportes',
        verbose_name='Reporte',
        null=True,
        blank=True
    )
    area = models.ForeignKey(
        'tickets.Area',
        on_delete=models.SET_NULL,
        related_name='sla_reportes',
        verbose_name='Área',
        null=True,
        blank=True
    )
    sla = models.ForeignKey(
        'tickets.SLA',
        on_delete=models.SET_NULL,
        related_name='sla_reportes',
        verbose_name='SLA',
        null=True,
        blank=True
    )
    prioridad = models.ForeignKey(
        'tickets.Prioridad',
        on_delete=models.SET_NULL,
        related_name='sla_reportes',
        verbose_name='Prioridad',
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'sla_reporte'
        verbose_name = 'SLA Reporte'
        verbose_name_plural = 'SLA Reportes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"SLA Reporte - {self.area or 'Global'}"
