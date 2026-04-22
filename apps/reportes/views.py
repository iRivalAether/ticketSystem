"""
Vistas del módulo de reportes.
"""
import csv
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import timezone

from apps.tickets.models import Ticket


def _normalizar_fecha(fecha_str):
    if not fecha_str:
        return None

    try:
        fecha = datetime.fromisoformat(fecha_str)
    except ValueError:
        return None

    if timezone.is_naive(fecha):
        fecha = timezone.make_aware(fecha, timezone.get_current_timezone())

    return fecha


def _obtener_rango_fechas(request):
    periodo = request.GET.get('periodo', '30d')
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')
    now = timezone.now()

    if periodo == '1d':
        return now.replace(hour=0, minute=0, second=0, microsecond=0), now
    if periodo == '7d':
        return now - timedelta(days=7), now
    if periodo == '30d':
        return now - timedelta(days=30), now
    if periodo == 'custom':
        fecha_inicio = _normalizar_fecha(fecha_inicio_str)
        fecha_fin = _normalizar_fecha(fecha_fin_str)
        if fecha_inicio and fecha_fin:
            return fecha_inicio, fecha_fin

    return now - timedelta(days=30), now


def _aplicar_filtros_tickets(request):
    fecha_inicio, fecha_fin = _obtener_rango_fechas(request)
    area_id = request.GET.get('area')
    jornada_id = request.GET.get('jornada')
    prioridad_id = request.GET.get('prioridad')

    tickets_qs = Ticket.objects.filter(
        created_at__gte=fecha_inicio,
        created_at__lte=fecha_fin,
        is_active=True,
    ).select_related('area', 'jornada', 'prioridad', 'sla', 'usuario_asignado')

    if area_id:
        tickets_qs = tickets_qs.filter(area_id=area_id)
    if jornada_id:
        tickets_qs = tickets_qs.filter(jornada_id=jornada_id)
    if prioridad_id:
        tickets_qs = tickets_qs.filter(prioridad_id=prioridad_id)

    return tickets_qs, fecha_inicio, fecha_fin


@login_required
def descargar_reporte_csv(request):
    """Descarga un reporte CSV con el filtro actual."""
    if not request.user.puede_ver_reportes_globales():
        messages.error(request, 'No tiene permisos para descargar reportes.')
        return redirect('dashboard')

    tickets_qs, fecha_inicio, fecha_fin = _aplicar_filtros_tickets(request)
    tickets = list(tickets_qs)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="reporte_tickets_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Reporte de tickets'])
    writer.writerow(['Generado por', request.user.nombre])
    writer.writerow(['Fecha inicio', timezone.localtime(fecha_inicio).strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow(['Fecha fin', timezone.localtime(fecha_fin).strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow([])
    writer.writerow([
        'Folio', 'Título', 'Estado', 'Área', 'Prioridad', 'Jornada', 'SLA',
        'SLA Estado', 'Creado', 'Inicio Atención', 'Cierre',
        'Primera Atención (min)', 'Resolución (h)'
    ])

    for ticket in tickets:
        writer.writerow([
            ticket.folio,
            ticket.nombre,
            ticket.estado,
            ticket.area.nombre if ticket.area else '',
            ticket.prioridad.nombre if ticket.prioridad else '',
            ticket.jornada.nombre if ticket.jornada else '',
            ticket.sla.nombre if ticket.sla else '',
            ticket.sla_status,
            timezone.localtime(ticket.created_at).strftime('%Y-%m-%d %H:%M:%S'),
            timezone.localtime(ticket.fecha_inicio_atencion).strftime('%Y-%m-%d %H:%M:%S') if ticket.fecha_inicio_atencion else '',
            timezone.localtime(ticket.fecha_cierre).strftime('%Y-%m-%d %H:%M:%S') if ticket.fecha_cierre else '',
            ticket.tiempo_primera_atencion_minutos or '',
            ticket.tiempo_resolucion_horas or '',
        ])

    return response