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

    return {
        'mis_tickets_abiertos': base_tickets.exclude(
            estado__in=[Ticket.ESTADO_CERRADO, Ticket.ESTADO_CERRADO_AUTOMATICO]
        ).count(),
        'tickets_en_atencion': base_tickets.filter(
            estado=Ticket.ESTADO_EN_ATENCION,
            usuario_asignado=usuario
        ).count(),
        'tickets_sla_critico': sum(1 for ticket in base_tickets if ticket.sla_status == 'rojo'),
        'cumplimiento_sla': metricas_sla['cumplimiento_porcentaje'],
        'promedio_primera_atencion': metricas_tiempos['promedio_primera_atencion_minutos'],
        'promedio_resolucion': metricas_tiempos['promedio_resolucion_horas'],
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
            tickets_jornada = Ticket.objects.filter(jornada=jornada)
            total = tickets_jornada.count()
            cumplimiento = 80  # Calcular dinámicamente
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
    
    context = {
        'stats_sla': stats_sla,
        'stats_tiempos': stats_tiempos,
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
