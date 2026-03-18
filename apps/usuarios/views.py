"""
Vistas para gestión de usuarios
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator

from apps.usuarios.models import Usuario
from apps.usuarios.forms import UsuarioCrearForm, UsuarioEditarForm


@login_required
def usuario_listar(request):
    """Lista todos los usuarios (solo Supervisores)"""
    if not request.user.es_supervision_general:
        messages.error(request, 'No tiene permisos para acceder a esta sección.')
        return redirect('dashboard')
    
    usuarios = Usuario.objects.all().select_related('rol')
    
    # Filtros
    rol_id = request.GET.get('rol')
    area_id = request.GET.get('area')
    activo = request.GET.get('activo')
    
    if rol_id:
        usuarios = usuarios.filter(rol_id=rol_id)
    
    if area_id:
        usuarios = usuarios.filter(area_id=area_id)
    
    if activo is not None:
        usuarios = usuarios.filter(is_active=activo == 'true')
    
    # Paginación
    paginator = Paginator(usuarios, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    from apps.tickets.models import Area
    from apps.usuarios.models import Rol
    
    context = {
        'page_obj': page_obj,
        'paginator': paginator,
        'is_paginated': page_obj.has_other_pages(),
        'roles': Rol.objects.filter(is_active=True),
        'areas': Area.objects.filter(is_active=True),
    }
    
    return render(request, 'usuarios/usuario_listar.html', context)


@login_required
def usuario_crear(request):
    """Crear un nuevo usuario (solo Supervisores)"""
    if not request.user.es_supervision_general:
        messages.error(request, 'No tiene permisos para crear usuarios.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UsuarioCrearForm(request.POST)
        if form.is_valid():
            try:
                # Crear usuario en Django
                user = User.objects.create_user(
                    username=form.cleaned_data['email'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'],
                    first_name=form.cleaned_data['nombre'].split()[0] if form.cleaned_data['nombre'] else '',
                    last_name=' '.join(form.cleaned_data['nombre'].split()[1:]) if len(form.cleaned_data['nombre'].split()) > 1 else '',
                )
                
                # Crear usuario extendido
                usuario = Usuario.objects.create(
                    user=user,
                    nombre=form.cleaned_data['nombre'],
                    rol=form.cleaned_data['rol'],
                    area=form.cleaned_data.get('area'),
                )
                
                messages.success(
                    request,
                    f'Usuario {usuario.nombre} ({usuario.rol.nombre}) creado exitosamente.'
                )
                return redirect('usuario_listar')
            except Exception as e:
                messages.error(request, f'Error al crear el usuario: {str(e)}')
    else:
        form = UsuarioCrearForm()
    
    context = {
        'form': form,
        'titulo': 'Crear nuevo usuario',
    }
    
    return render(request, 'usuarios/usuario_form.html', context)


@login_required
def usuario_editar(request, usuario_id):
    """Editar usuario (solo Supervisores)"""
    if not request.user.es_supervision_general:
        messages.error(request, 'No tiene permisos para editar usuarios.')
        return redirect('dashboard')
    
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    if request.method == 'POST':
        form = UsuarioEditarForm(request.POST, instance=usuario)
        if form.is_valid():
            try:
                form.save()
                messages.success(
                    request,
                    f'Usuario {usuario.nombre} actualizado exitosamente.'
                )
                return redirect('usuario_listar')
            except Exception as e:
                messages.error(request, f'Error al actualizar el usuario: {str(e)}')
    else:
        form = UsuarioEditarForm(instance=usuario)
    
    context = {
        'form': form,
        'usuario': usuario,
        'titulo': f'Editar usuario: {usuario.nombre}',
    }
    
    return render(request, 'usuarios/usuario_form.html', context)


@login_required
def usuario_detalle(request, usuario_id):
    """Ver detalles de un usuario"""
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    # Validar permisos
    if not (request.user.es_supervision_general or request.user == usuario):
        messages.error(request, 'No tiene permisos para ver este usuario.')
        return redirect('dashboard')
    
    # Estadísticas del usuario si es operativo
    stats = {}
    if usuario.es_operativo and usuario:
        from services.ticket_service import TicketService
        mis_tickets = TicketService.obtener_tickets_por_usuario(usuario)
        stats = {
            'tickets_totales': mis_tickets.count(),
            'tickets_abiertos': mis_tickets.filter(estado='Abierto').count(),
            'tickets_asignados': mis_tickets.filter(estado='Asignado').count(),
            'tickets_en_atencion': mis_tickets.filter(estado='En Atención').count(),
        }
    
    context = {
        'usuario': usuario,
        'stats': stats,
    }
    
    return render(request, 'usuarios/usuario_detalle.html', context)
