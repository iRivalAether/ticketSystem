"""
Servicio de Reportes - Generación de reportes y KPIs

Pattern: Service Layer Pattern
Responsabilidades:
- Generación de reportes
- Cálculo de KPIs
- Análisis de métricas
"""
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from django.db.models import Avg, Count, Q, F, ExpressionWrapper, DurationField

from apps.reportes.models import Reporte, KPI, SLAReporte
from apps.tickets.models import Ticket, Area, Prioridad, SLA, Jornada

logger = logging.getLogger(__name__)


class ReporteService:
    """
    Servicio para generación de reportes y KPIs
    Pattern: Service Layer + Builder
    """
    
    @staticmethod
    @transaction.atomic
    def generar_reporte_semanal(usuario, area=None):
        """
        Genera un reporte semanal
        
        Args:
            usuario (Usuario): Usuario que genera el reporte
            area (Area): Área específica (opcional, None = reporte global)
        
        Returns:
            Reporte: El reporte generado con sus KPIs
        """
        # Validar permisos
        if usuario.es_operativo and area is None:
            from django.core.exceptions import ValidationError
            raise ValidationError('Usuarios operativos no pueden generar reportes globales')
        
        # Crear reporte
        reporte = Reporte.objects.create(
            tipo=Reporte.TIPO_SEMANAL,
            generado_por_usuario=usuario,
            area=area
        )
        
        # Calcular período (última semana)
        fecha_fin = timezone.now()
        fecha_inicio = fecha_fin - timedelta(days=7)
        
        # Generar KPIs
        kpis = ReporteService._calcular_kpis(area, fecha_inicio, fecha_fin)
        
        # Guardar KPIs
        KPI.objects.create(
            reporte=reporte,
            tiempo_promedio_atencion=kpis['tiempo_promedio_atencion'],
            tiempo_promedio_resolucion=kpis['tiempo_promedio_resolucion'],
            cumplimiento_sla=kpis['cumplimiento_sla']
        )
        
        logger.info(f"Reporte semanal generado por {usuario.nombre} - Área: {area or 'Global'}")
        
        return reporte
    
    @staticmethod
    @transaction.atomic
    def generar_reporte_mensual(usuario, area=None):
        """
        Genera un reporte mensual
        
        Args:
            usuario (Usuario): Usuario que genera el reporte
            area (Area): Área específica (opcional)
        
        Returns:
            Reporte: El reporte generado
        """
        # Crear reporte
        reporte = Reporte.objects.create(
            tipo=Reporte.TIPO_MENSUAL,
            generado_por_usuario=usuario,
            area=area
        )
        
        # Calcular período (último mes)
        fecha_fin = timezone.now()
        fecha_inicio = fecha_fin - timedelta(days=30)
        
        # Generar KPIs
        kpis = ReporteService._calcular_kpis(area, fecha_inicio, fecha_fin)
        
        # Guardar KPIs
        KPI.objects.create(
            reporte=reporte,
            tiempo_promedio_atencion=kpis['tiempo_promedio_atencion'],
            tiempo_promedio_resolucion=kpis['tiempo_promedio_resolucion'],
            cumplimiento_sla=kpis['cumplimiento_sla']
        )
        
        logger.info(f"Reporte mensual generado por {usuario.nombre} - Área: {area or 'Global'}")
        
        return reporte
    
    @staticmethod
    def _calcular_kpis(area, fecha_inicio, fecha_fin):
        """
        Calcula KPIs para un período específico
        
        Args:
            area (Area): Área a analizar (None = global)
            fecha_inicio (datetime): Inicio del período
            fecha_fin (datetime): Fin del período
        
        Returns:
            dict: KPIs calculados
        """
        # Filtrar tickets
        queryset = Ticket.objects.filter(
            fecha_creacion__gte=fecha_inicio,
            fecha_creacion__lte=fecha_fin,
            is_active=True
        )
        
        if area:
            queryset = queryset.filter(area=area)
        
        # Calcular tiempo promedio de atención (tiempo hasta primer cambio a "En Atención")
        tickets_en_atencion = queryset.filter(
            fecha_inicio_atencion__isnull=False
        )
        
        if tickets_en_atencion.exists():
            tiempo_promedio_atencion_seconds = 0
            count_atencion = 0
            
            for ticket in tickets_en_atencion:
                if ticket.fecha_inicio_atencion:
                    tiempo_atencion = (ticket.fecha_inicio_atencion - ticket.fecha_creacion).total_seconds() / 60
                    tiempo_promedio_atencion_seconds += tiempo_atencion
                    count_atencion += 1
            
            tiempo_promedio_atencion = tiempo_promedio_atencion_seconds / count_atencion if count_atencion > 0 else 0
        else:
            tiempo_promedio_atencion = 0
        
        # Calcular tiempo promedio de resolución (tiempo hasta cierre)
        tickets_cerrados = queryset.filter(
            estado__in=[Ticket.ESTADO_CERRADO, Ticket.ESTADO_CERRADO_AUTOMATICO],
            fecha_cierre__isnull=False
        )
        
        if tickets_cerrados.exists():
            tiempo_promedio_resolucion_hours = 0
            count_resolucion = 0
            
            for ticket in tickets_cerrados:
                if ticket.fecha_cierre:
                    tiempo_resolucion = (ticket.fecha_cierre - ticket.fecha_creacion).total_seconds() / 3600
                    tiempo_promedio_resolucion_hours += tiempo_resolucion
                    count_resolucion += 1
            
            tiempo_promedio_resolucion = tiempo_promedio_resolucion_hours / count_resolucion if count_resolucion > 0 else 0
        else:
            tiempo_promedio_resolucion = 0
        
        # Calcular cumplimiento de SLA
        total_tickets = queryset.count()
        
        if total_tickets > 0:
            tickets_cumplen_sla = 0
            
            for ticket in queryset:
                if ticket.sla_status == 'verde' or ticket.estado in [Ticket.ESTADO_CERRADO, Ticket.ESTADO_CERRADO_AUTOMATICO]:
                    # Verificar si se cerró dentro del SLA
                    if ticket.fecha_cierre and ticket.tiempo_limite_resolucion:
                        if ticket.fecha_cierre <= ticket.tiempo_limite_resolucion:
                            tickets_cumplen_sla += 1
                    elif ticket.sla_status == 'verde':
                        tickets_cumplen_sla += 1
            
            cumplimiento_sla = (tickets_cumplen_sla / total_tickets) * 100
        else:
            cumplimiento_sla = 0
        
        return {
            'tiempo_promedio_atencion': round(tiempo_promedio_atencion, 2),
            'tiempo_promedio_resolucion': round(tiempo_promedio_resolucion, 2),
            'cumplimiento_sla': round(cumplimiento_sla, 2),
            'total_tickets': total_tickets,
        }
    
    @staticmethod
    def obtener_estadisticas_por_jornada(fecha_inicio, fecha_fin, area=None):
        """
        Obtiene estadísticas de tickets por jornada
        
        Args:
            fecha_inicio (datetime): Inicio del período
            fecha_fin (datetime): Fin del período
            area (Area): Área específica (opcional)
        
        Returns:
            dict: Estadísticas por jornada
        """
        queryset = Ticket.objects.filter(
            fecha_creacion__gte=fecha_inicio,
            fecha_creacion__lte=fecha_fin,
            is_active=True
        )
        
        if area:
            queryset = queryset.filter(area=area)
        
        estadisticas = {}
        
        for jornada_tipo in [Jornada.MATUTINA, Jornada.VESPERTINA, Jornada.NOCTURNA]:
            tickets_jornada = queryset.filter(jornada__nombre=jornada_tipo)
            
            estadisticas[jornada_tipo] = {
                'total_tickets': tickets_jornada.count(),
                'tickets_cerrados': tickets_jornada.filter(
                    estado__in=[Ticket.ESTADO_CERRADO, Ticket.ESTADO_CERRADO_AUTOMATICO]
                ).count(),
                'tickets_abiertos': tickets_jornada.filter(estado=Ticket.ESTADO_ABIERTO).count(),
                'tickets_en_atencion': tickets_jornada.filter(estado=Ticket.ESTADO_EN_ATENCION).count(),
            }
        
        return estadisticas
    
    @staticmethod
    def obtener_estadisticas_por_area(fecha_inicio, fecha_fin):
        """
        Obtiene estadísticas comparativas por área
        
        Args:
            fecha_inicio (datetime): Inicio del período
            fecha_fin (datetime): Fin del período
        
        Returns:
            dict: Estadísticas por área
        """
        areas = Area.objects.filter(is_active=True)
        estadisticas = {}
        
        for area in areas:
            kpis = ReporteService._calcular_kpis(area, fecha_inicio, fecha_fin)
            estadisticas[area.nombre] = kpis
        
        return estadisticas
