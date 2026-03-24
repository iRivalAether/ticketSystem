from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from datetime import datetime, timedelta

from apps.tickets.models import Ticket, Area, Prioridad, Jornada, SemaforoSLAConfig
from apps.tickets.forms import TicketCreateForm, TicketTriajeForm, TicketCerrarForm, SemaforoSLAConfigForm
from services.ticket_service import TicketService


def _build_dashboard_metrics(usuario):
    area_referencia = usuario.area if usuario.es_jefe_area else None
    base_tickets = TicketService.obtener_tickets_por_usuario(usuario)
    metricas_tiempos = TicketService.obtener_promedios_tiempos(area=area_referencia)
    metricas_sla = TicketService.obtener_estadisticas_sla(area=area_referencia)

    if usuario.es_operativo:
        tickets_en_atencion = base_tickets.filter(
            estado=Ticket.ESTADO_EN_ATENCION,
            usuario_asignado=usuario
        )
    else:
        tickets_en_atencion = base_tickets.filter(estado=Ticket.ESTADO_EN_ATENCION)
    
    tickets_abiertos = base_tickets.exclude(
        estado__in=[Ticket.ESTADO_CERRADO, Ticket.ESTADO_CERRADO_AUTOMATICO]
    )
    tickets_asignados = base_tickets.filter(estado=Ticket.ESTADO_ASIGNADO)

    return {
        'mis_tickets_abiertos': tickets_abiertos.count(),
        'mis_tickets_asignados': tickets_asignados.count(),
        'tickets_en_atencion': tickets_en_atencion.count(),
        'tickets_total_activos': base_tickets.exclude(
            estado__in=[Ticket.ESTADO_CERRADO, Ticket.ESTADO_CERRADO_AUTOMATICO]
        ).count(),
        'tickets_sla_critico': metricas_sla['sla_rojo'],
        'tickets_sla_alerta': metricas_sla['sla_amarillo'],
        'tickets_sla_ok': metricas_sla['sla_verde'],
        'cumplimiento_sla': metricas_sla['cumplimiento_porcentaje'],
        'promedio_primera_atencion': metricas_tiempos['promedio_primera_atencion_minutos'],
        'promedio_resolucion': metricas_tiempos['promedio_resolucion_horas'],
        'tickets_cerrados_total': metricas_sla['total_cerrados'],
    }


@login_required
def dashboard(request):
    """Vista principal del dashboard"""
    usuario = request.user
    
    # Obtener tickets según nivel jerárquico
    mis_tickets = TicketService.obtener_tickets_por_usuario(usuario).exclude(
        estado__in=[Ticket.ESTADO_CERRADO, Ticket.ESTADO_CERRADO_AUTOMATICO]
    )[:10]

    stats = _build_dashboard_metrics(usuario)
    
    # Próximo ticket FIFO
    proximo_ticket = None
    if usuario.rol.nivel_jerarquico == 1:  # Operativo
        proximo_ticket = TicketService.obtener_proximo_ticket_fifo(area=usuario.area)
    
    # Tickets pendientes de triaje para Jefes de Área
    tickets_triaje = None
    if usuario.puede_asignar_ticket():
        tickets_triaje = Ticket.objects.filter(
            estado=Ticket.ESTADO_ABIERTO,
            area__isnull=True
        ).order_by('created_at')[:5]
    
    # Estadísticas por jornada para Supervisión General
    stats_jornada = None
    if usuario.puede_ver_reportes_globales():
        stats_jornada = []
        for jornada in Jornada.objects.all():
            tickets_jornada = Ticket.objects.filter(jornada=jornada, is_active=True)
            total = tickets_jornada.count()

            tickets_cerrados = tickets_jornada.filter(
                estado__in=[Ticket.ESTADO_CERRADO, Ticket.ESTADO_CERRADO_AUTOMATICO],
                fecha_cierre__isnull=False
            )
            total_cerrados = tickets_cerrados.count()
            cerrados_en_tiempo = 0

            for ticket in tickets_cerrados:
                if ticket.tiempo_limite_resolucion and ticket.fecha_cierre <= ticket.tiempo_limite_resolucion:
                    cerrados_en_tiempo += 1

            cumplimiento = round((cerrados_en_tiempo / total_cerrados) * 100, 2) if total_cerrados else 0
            stats_jornada.append({
                'jornada': jornada.nombre,
                'total': total,
                'cumplimiento': cumplimiento
            })
    
    context = {
        'stats': stats,
        'mis_tickets': mis_tickets,
        'proximo_ticket': proximo_ticket,
        'tickets_triaje': tickets_triaje,
        'stats_jornada': stats_jornada,
        'semaforo_config': SemaforoSLAConfig.get_default_config(),
    }
    
    return render(request, 'dashboard.html', context)


@login_required
def ticket_list(request):
    """Lista de tickets con filtros"""
    usuario = request.user
    
    # Base queryset según permisos
    tickets = TicketService.obtener_tickets_por_usuario(usuario)
    
    # Filtros
    estado = request.GET.get('estado')
    area_id = request.GET.get('area')
    prioridad_id = request.GET.get('prioridad')
    sla_status = request.GET.get('sla')
    
    if estado:
        tickets = tickets.filter(estado=estado)
    
    if area_id:
        tickets = tickets.filter(area_id=area_id)
    
    if prioridad_id:
        tickets = tickets.filter(prioridad_id=prioridad_id)

    if sla_status in ['verde', 'amarillo', 'rojo']:
        ticket_ids = [ticket.id for ticket in tickets if ticket.sla_status == sla_status]
        tickets = tickets.filter(id__in=ticket_ids)
    
    # Paginación
    paginator = Paginator(tickets, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tickets': page_obj,
        'page_obj': page_obj,
        'paginator': paginator,
        'is_paginated': page_obj.has_other_pages(),
        'areas': Area.objects.filter(is_active=True),
        'prioridades': Prioridad.objects.filter(is_active=True),
    }
    
    return render(request, 'tickets/ticket_list.html', context)


@login_required
def ticket_detail(request, ticket_id):
    """Detalle de un ticket"""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    # Verificar permisos
    if not request.user.puede_ver_ticket(ticket):
        messages.error(request, 'No tiene permisos para ver este ticket.')
        return redirect('dashboard')
    
    # Obtener historial
    historial_estados = ticket.historial_estados.all().order_by('-fecha')
    
    context = {
        'ticket': ticket,
        'historial_estados': historial_estados,
    }
    
    return render(request, 'tickets/ticket_detail.html', context)


@login_required
def ticket_crear(request):
    """Crear un nuevo ticket"""
    if request.method == 'POST':
        form = TicketCreateForm(request.POST)
        if form.is_valid():
            try:
                prioridad = form.cleaned_data['prioridad']
                
                # Obtener el SLA correspondiente a la prioridad
                # Asumiendo que el nivel de prioridad coincide con el nivel del SLA
                from apps.tickets.models import SLA
                sla = SLA.objects.filter(is_active=True).order_by('tiempo_respuesta')[prioridad.nivel - 1]
                
                # Preparar datos para el servicio
                datos = {
                    'nombre': form.cleaned_data['nombre'],
                    'descripcion': form.cleaned_data['descripcion'],
                    'prioridad_id': prioridad.id,
                    'sla_id': sla.id,
                }
                
                # Usar el servicio para crear el ticket
                ticket = TicketService.crear_ticket(
                    datos=datos,
                    usuario_creador=request.user
                )
                messages.success(
                    request,
                    f'Ticket {ticket.folio} creado exitosamente.'
                )
                return redirect('ticket_detalle', ticket_id=ticket.id)
            except Exception as e:
                messages.error(request, f'Error al crear el ticket: {str(e)}')
    else:
        form = TicketCreateForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'tickets/ticket_form.html', context)


@login_required
def ticket_triaje(request):
    """Lista de tickets pendientes de triaje"""
    if not request.user.puede_asignar_ticket():
        messages.error(request, 'No tiene permisos para realizar triaje.')
        return redirect('dashboard')
    
    tickets = Ticket.objects.filter(
        estado=Ticket.ESTADO_ABIERTO,
        area__isnull=True
    ).order_by('created_at')
    
    context = {
        'tickets': tickets,
    }
    
    return render(request, 'tickets/ticket_triaje_list.html', context)


@login_required
def ticket_realizar_triaje(request, ticket_id):
    """Realizar triaje de un ticket"""
    if not request.user.puede_asignar_ticket():
        messages.error(request, 'No tiene permisos para realizar triaje.')
        return redirect('dashboard')
    
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    if request.method == 'POST':
        form = TicketTriajeForm(request.POST, jefe_area=request.user)
        if form.is_valid():
            try:
                area = form.cleaned_data['area']

                if request.user.es_jefe_area and request.user.area and area.id != request.user.area_id:
                    messages.error(request, 'Solo puede asignar tickets a su propia área.')
                    return redirect('ticket_realizar_triaje', ticket_id=ticket.id)
                
                # Realizar triaje (mantiene la prioridad actual del ticket)
                TicketService.realizar_triaje(
                    ticket_id=ticket.id,
                    area_id=area.id,
                    prioridad_id=ticket.prioridad.id,
                    jefe_area=request.user
                )
                
                # Asignar si se seleccionó usuario
                if form.cleaned_data.get('usuario_asignado'):
                    usuario_asignado = form.cleaned_data['usuario_asignado']
                    comentario = form.cleaned_data.get('comentario', '')
                    TicketService.asignar_ticket(
                        ticket_id=ticket.id,
                        usuario_asignado_id=usuario_asignado.id,
                        jefe_area=request.user,
                        motivo=comentario
                    )
                
                messages.success(
                    request,
                    f'Triaje realizado exitosamente para {ticket.folio}.'
                )
                return redirect('ticket_triaje')
            except Exception as e:
                messages.error(request, f'Error al realizar triaje: {str(e)}')
    else:
        form = TicketTriajeForm(jefe_area=request.user)
    
    context = {
        'ticket': ticket,
        'form': form,
    }
    
    return render(request, 'tickets/ticket_triaje_form.html', context)


@login_required
def semaforo_config(request):
    """Configuración de umbrales del semáforo SLA (Admin y Jefes de Área)."""
    if not (request.user.is_superuser or request.user.es_jefe_area):
        messages.error(request, 'No tiene permisos para configurar semáforos SLA.')
        return redirect('dashboard')

    config = SemaforoSLAConfig.get_default_config()

    if request.method == 'POST':
        form = SemaforoSLAConfigForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuración de semáforo SLA actualizada correctamente.')
            return redirect('semaforo_config')
    else:
        form = SemaforoSLAConfigForm(instance=config)

    context = {
        'form': form,
        'config_actual': config,
    }
    return render(request, 'tickets/semaforo_config.html', context)


@login_required
def ticket_atencion(request, ticket_id):
    """Iniciar atención de un ticket"""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    if ticket.usuario_asignado != request.user:
        messages.error(request, 'Este ticket no está asignado a usted.')
        return redirect('dashboard')
    
    try:
        TicketService.iniciar_atencion_ticket(
            ticket_id=ticket.id,
            usuario_operativo=request.user
        )
        messages.success(
            request,
            f'Atención iniciada para {ticket.folio}.'
        )
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    
    return redirect('ticket_detalle', ticket_id=ticket.id)


@login_required
def ticket_cerrar(request, ticket_id):
    """Cerrar un ticket"""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    if ticket.usuario_asignado != request.user:
        messages.error(request, 'Este ticket no está asignado a usted.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = TicketCerrarForm(request.POST)
        if form.is_valid():
            try:
                TicketService.cerrar_ticket(
                    ticket_id=ticket.id,
                    usuario=request.user,
                    comentario=form.cleaned_data['solucion']
                )
                messages.success(
                    request,
                    f'Ticket {ticket.folio} cerrado exitosamente.'
                )
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f'Error al cerrar ticket: {str(e)}')
    else:
        form = TicketCerrarForm()
    
    context = {
        'ticket': ticket,
        'form': form,
    }
    
    return render(request, 'tickets/ticket_cerrar.html', context)


@login_required
def reportes(request):
    """Vista de reportes (solo Supervisión General)"""
    if not request.user.puede_ver_reportes_globales():
        messages.error(request, 'No tiene permisos para ver reportes.')
        return redirect('dashboard')
    
    # Calcular estadísticas
    stats_sla = TicketService.obtener_estadisticas_sla()
    stats_tiempos = TicketService.obtener_promedios_tiempos()
    
    # Obtener catálogos para filtros
    areas = Area.objects.filter(is_active=True)
    jornadas = Jornada.objects.filter(is_active=True)
    prioridades = Prioridad.objects.filter(is_active=True)
    
    context = {
        'stats_sla': stats_sla,
        'stats_tiempos': stats_tiempos,
        'areas': areas,
        'jornadas': jornadas,
        'prioridades': prioridades,
    }
    
    return render(request, 'reportes/dashboard.html', context)


@login_required
def dashboard_stats_api(request):
    """Endpoint AJAX para refrescar métricas del dashboard."""
    payload = _build_dashboard_metrics(request.user)
    payload['semaforo_config'] = {
        'warning_percentage': SemaforoSLAConfig.get_default_config().warning_percentage,
        'danger_percentage': SemaforoSLAConfig.get_default_config().danger_percentage,
    }
    return JsonResponse(payload)


@login_required
def reportes_stats_api(request):
    """Endpoint AJAX para refrescar métricas globales de reportes."""
    if not request.user.puede_ver_reportes_globales():
        return JsonResponse({'error': 'No autorizado'}, status=403)

    stats_sla = TicketService.obtener_estadisticas_sla()
    stats_tiempos = TicketService.obtener_promedios_tiempos()

    return JsonResponse({
        'stats_sla': stats_sla,
        'stats_tiempos': stats_tiempos,
    })


@login_required
def ticket_liberar(request, ticket_id):
    """Liberar un ticket (cerrarlo por jefatura)."""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    # Solo jefe de área puede liberar
    if not request.user.es_jefe_area:
        messages.error(request, 'Solo el jefe de área puede liberar tickets.')
        return redirect('dashboard')

    # Jefe solo sobre su área
    if request.user.area and ticket.area_id != request.user.area_id:
        messages.error(request, 'Solo puede liberar tickets de su área.')
        return redirect('dashboard')
    
    if ticket.estado not in [Ticket.ESTADO_ASIGNADO, Ticket.ESTADO_EN_ATENCION]:
        messages.error(request, f'El ticket debe estar Asignado o En Atención. Estado actual: {ticket.estado}')
        return redirect('ticket_detalle', ticket_id=ticket.id)
    
    if request.method == 'POST':
        try:
            TicketService.liberar_ticket(ticket_id=ticket.id, usuario=request.user)
            messages.success(
                request,
                f'Ticket {ticket.folio} liberado y cerrado exitosamente.'
            )
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f'Error al liberar ticket: {str(e)}')
    
    context = {
        'ticket': ticket,
        'accion': 'liberar',
    }
    
    return render(request, 'tickets/ticket_liberar.html', context)


@login_required
def ticket_devolver(request, ticket_id):
    """Compatibilidad: redirige al flujo de retomar ticket."""
    return ticket_retomar(request, ticket_id)


@login_required
def ticket_retomar(request, ticket_id):
    """Retomar un ticket cerrado para continuar su atención."""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    # Solo jefe de área
    if not request.user.es_jefe_area:
        messages.error(request, 'Solo el jefe de área puede retomar tickets.')
        return redirect('dashboard')

    # Jefe solo sobre su área
    if request.user.area and ticket.area_id != request.user.area_id:
        messages.error(request, 'Solo puede retomar tickets de su área.')
        return redirect('dashboard')
    
    if ticket.estado not in [Ticket.ESTADO_CERRADO, Ticket.ESTADO_CERRADO_AUTOMATICO]:
        messages.error(request, f'El ticket debe estar Cerrado. Estado actual: {ticket.estado}')
        return redirect('ticket_detalle', ticket_id=ticket.id)
    
    if request.method == 'POST':
        motivo = request.POST.get('motivo', '')
        try:
            TicketService.retomar_ticket(ticket_id=ticket.id, usuario=request.user, motivo=motivo)
            messages.success(
                request,
                f'Ticket {ticket.folio} retomado exitosamente.'
            )
            return redirect('ticket_detalle', ticket_id=ticket.id)
        except Exception as e:
            messages.error(request, f'Error al retomar ticket: {str(e)}')
    
    context = {
        'ticket': ticket,
        'accion': 'retomar',
    }
    
    return render(request, 'tickets/ticket_retomar.html', context)


@login_required
def reportes_datos_filtrados_api(request):
    """
    API para obtener datos de reportes con filtros.
    
    Query params:
    - periodo: '1d' (hoy), '7d' (últimos 7), '30d' (últimos 30), 'custom' (requiere fecha_inicio/fecha_fin)
    - fecha_inicio: formato ISO (solo si periodo=custom)
    - fecha_fin: formato ISO (solo si periodo=custom)
    - area: ID del área (opcional)
    - jornada: ID de la jornada (opcional)
    - prioridad: ID de la prioridad (opcional)
    """
    from django.utils import timezone
    
    # Validar permiso
    if not request.user.puede_ver_reportes_globales():
        return JsonResponse({'error': 'No tienes permiso'}, status=403)
    
    # Obtener filtros
    periodo = request.GET.get('periodo', '30d')
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')
    area_id = request.GET.get('area')
    jornada_id = request.GET.get('jornada')
    prioridad_id = request.GET.get('prioridad')
    
    # Calcular rango de fechas
    now = timezone.now()
    if periodo == '1d':
        fecha_inicio = now.replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = now
    elif periodo == '7d':
        fecha_inicio = now - timedelta(days=7)
        fecha_fin = now
    elif periodo == '30d':
        fecha_inicio = now - timedelta(days=30)
        fecha_fin = now
    elif periodo == 'custom' and fecha_inicio_str and fecha_fin_str:
        try:
            fecha_inicio = datetime.fromisoformat(fecha_inicio_str)
            fecha_fin = datetime.fromisoformat(fecha_fin_str)
        except:
            return JsonResponse({'error': 'Fechas inválidas'}, status=400)
    else:
        fecha_inicio = now - timedelta(days=30)
        fecha_fin = now
    
    # Construir queryset base
    tickets_qs = Ticket.objects.filter(
        created_at__gte=fecha_inicio,
        created_at__lte=fecha_fin,
        is_active=True
    ).select_related('area', 'jornada', 'prioridad', 'sla')
    
    # Aplicar filtros
    if area_id:
        tickets_qs = tickets_qs.filter(area_id=area_id)
    if jornada_id:
        tickets_qs = tickets_qs.filter(jornada_id=jornada_id)
    if prioridad_id:
        tickets_qs = tickets_qs.filter(prioridad_id=prioridad_id)

    tickets = list(tickets_qs)

    # Calcular estadísticas SLA y tiempos sobre tickets filtrados
    sla_verde = 0
    sla_amarillo = 0
    sla_rojo = 0
    tiempos_atencion = []
    tiempos_resolucion = []

    for ticket in tickets:
        if ticket.sla_status == 'rojo':
            sla_rojo += 1
        elif ticket.sla_status == 'amarillo':
            sla_amarillo += 1
        else:
            sla_verde += 1

        if ticket.tiempo_primera_atencion_minutos is not None:
            tiempos_atencion.append(ticket.tiempo_primera_atencion_minutos)
        if ticket.tiempo_resolucion_horas is not None:
            tiempos_resolucion.append(ticket.tiempo_resolucion_horas)

    total_tickets = len(tickets)
    cumplimiento_porcentaje = (sla_verde / total_tickets * 100) if total_tickets else 0

    stats_sla = {
        'total_tickets': total_tickets,
        'sla_verde': sla_verde,
        'sla_amarillo': sla_amarillo,
        'sla_rojo': sla_rojo,
        'cumplimiento_porcentaje': round(cumplimiento_porcentaje, 2),
    }

    stats_tiempos = {
        'promedio_primera_atencion_minutos': round(sum(tiempos_atencion) / len(tiempos_atencion), 2) if tiempos_atencion else 0,
        'promedio_resolucion_horas': round(sum(tiempos_resolucion) / len(tiempos_resolucion), 2) if tiempos_resolucion else 0,
    }

    # Desglosar por área, jornada, prioridad
    desglose_area = {}
    desglose_jornada = {}
    desglose_prioridad = {}

    for ticket in tickets:
        area_nombre = ticket.area.nombre if ticket.area else 'Sin área'
        jornada_nombre = ticket.jornada.nombre if ticket.jornada else 'Sin jornada'
        prioridad_nombre = ticket.prioridad.nombre if ticket.prioridad else 'Sin prioridad'
        estado_sla = ticket.sla_status

        if area_nombre not in desglose_area:
            desglose_area[area_nombre] = {'total': 0, 'verde': 0, 'amarillo': 0, 'rojo': 0}
        if jornada_nombre not in desglose_jornada:
            desglose_jornada[jornada_nombre] = {'total': 0, 'verde': 0, 'amarillo': 0, 'rojo': 0}
        if prioridad_nombre not in desglose_prioridad:
            desglose_prioridad[prioridad_nombre] = {'total': 0, 'verde': 0, 'amarillo': 0, 'rojo': 0}

        desglose_area[area_nombre]['total'] += 1
        desglose_jornada[jornada_nombre]['total'] += 1
        desglose_prioridad[prioridad_nombre]['total'] += 1

        if estado_sla == 'rojo':
            desglose_area[area_nombre]['rojo'] += 1
            desglose_jornada[jornada_nombre]['rojo'] += 1
            desglose_prioridad[prioridad_nombre]['rojo'] += 1
        elif estado_sla == 'amarillo':
            desglose_area[area_nombre]['amarillo'] += 1
            desglose_jornada[jornada_nombre]['amarillo'] += 1
            desglose_prioridad[prioridad_nombre]['amarillo'] += 1
        else:
            desglose_area[area_nombre]['verde'] += 1
            desglose_jornada[jornada_nombre]['verde'] += 1
            desglose_prioridad[prioridad_nombre]['verde'] += 1

    # Series temporales (por hora, últimas 24 horas)
    series_temporal = []
    hora_base = now.replace(minute=0, second=0, microsecond=0) - timedelta(hours=23)
    for i in range(24):
        hora_inicio = hora_base + timedelta(hours=i)
        hora_fin = hora_inicio + timedelta(hours=1)
        count = sum(1 for ticket in tickets if hora_inicio <= ticket.created_at < hora_fin)
        series_temporal.append({
            'hora': hora_inicio.isoformat(),
            'count': count
        })

    # Heatmap: carga por jornada y hora (24 columnas)
    jornadas_activas = list(Jornada.objects.filter(is_active=True).values_list('nombre', flat=True))
    heatmap_jornada = {nombre: [0] * 24 for nombre in jornadas_activas}

    for ticket in tickets:
        jornada_nombre = ticket.jornada.nombre if ticket.jornada else 'Sin jornada'
        if jornada_nombre not in heatmap_jornada:
            heatmap_jornada[jornada_nombre] = [0] * 24
        hora_ticket = ticket.created_at.astimezone(timezone.get_current_timezone()).hour
        heatmap_jornada[jornada_nombre][hora_ticket] += 1
    
    return JsonResponse({
        'periodo': {
            'inicio': fecha_inicio.isoformat(),
            'fin': fecha_fin.isoformat()
        },
        'estadisticas': {
            'sla': stats_sla,
            'tiempos': stats_tiempos,
            'total_tickets': total_tickets,
        },
        'desglose': {
            'por_area': desglose_area,
            'por_jornada': desglose_jornada,
            'por_prioridad': desglose_prioridad,
        },
        'series_temporal': series_temporal,
        'heatmap_jornada': heatmap_jornada,
    })


@login_required
def actividades_recientes_api(request):
    """
    API para obtener cambios recientes de tickets y usuarios.
    Útil para detectar cambios en tiempo real.
    """
    from apps.tickets.models import TicketEstadoHistorial
    
    limit = int(request.GET.get('limit', 10))
    
    # Historial de cambios de estado
    cambios = TicketEstadoHistorial.objects.select_related(
        'ticket', 'usuario'
    ).order_by('-created_at')[:limit]
    
    cambios_data = []
    for cambio in cambios:
        cambios_data.append({
            'ticket_id': cambio.ticket.id,
            'ticket_numero': cambio.ticket.numero,
            'usuario': cambio.usuario.nombre,
            'estado_anterior': cambio.estado_anterior,
            'estado_nuevo': cambio.estado_nuevo,
            'timestamp': cambio.created_at.isoformat(),
        })
    
    return JsonResponse({
        'cambios_recientes': cambios_data,
        'total': len(cambios_data),
    })
