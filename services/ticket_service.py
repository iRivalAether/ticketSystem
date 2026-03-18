"""
Servicio de Tickets - Lógica de negocio centralizada

Pattern: Service Layer Pattern
Responsabilidades:
- Validaciones de negocio
- Orquestación de operaciones complejas
- Coordinación entre múltiples modelos
- Implementación de reglas de negocio
"""
import logging
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from django.core.exceptions import ValidationError

from apps.tickets.models import (
    Ticket, TicketEstadoHistorial, TicketAsignacionHistorial,
    Area, Prioridad, SLA, Jornada
)

logger = logging.getLogger(__name__)


class TicketService:
    """
    Servicio para gestión de tickets
    Pattern: Service Layer + Facade
    """
    
    @staticmethod
    @transaction.atomic
    def crear_ticket(datos, usuario_creador=None):
        """
        Crea un nuevo ticket en el sistema
        
        Args:
            datos (dict): Datos del ticket (nombre, descripcion, prioridad_id, sla_id, jornada_id)
            usuario_creador (Usuario): Usuario que crea el ticket
        
        Returns:
            Ticket: El ticket creado
        
        Raises:
            ValidationError: Si los datos no son válidos
        """
        # Validaciones de negocio
        if not datos.get('nombre'):
            raise ValidationError('El nombre del ticket es obligatorio')
        
        if not datos.get('prioridad_id'):
            raise ValidationError('La prioridad es obligatoria')
        
        if not datos.get('sla_id'):
            raise ValidationError('El SLA es obligatorio')
        
        # Determinar jornada actual si no se especifica
        jornada = datos.get('jornada_id')
        if not jornada:
            jornada = TicketService._determinar_jornada_actual()
        
        # Crear el ticket
        ticket = Ticket.objects.create(
            nombre=datos['nombre'],
            descripcion=datos.get('descripcion', ''),
            prioridad_id=datos['prioridad_id'],
            sla_id=datos['sla_id'],
            jornada_id=jornada if isinstance(jornada, int) else jornada.id,
            estado=Ticket.ESTADO_ABIERTO
        )
        
        logger.info(f"Ticket {ticket.folio} creado por {usuario_creador}")
        
        return ticket
    
    @staticmethod
    def _determinar_jornada_actual():
        """
        Determina la jornada actual basándose en la hora
        
        Returns:
            Jornada: La jornada correspondiente a la hora actual
        """
        hora_actual = timezone.now().hour
        
        if 6 <= hora_actual < 14:
            jornada_nombre = Jornada.MATUTINA
        elif 14 <= hora_actual < 22:
            jornada_nombre = Jornada.VESPERTINA
        else:
            jornada_nombre = Jornada.NOCTURNA
        
        jornada, _ = Jornada.objects.get_or_create(nombre=jornada_nombre)
        return jornada
    
    @staticmethod
    @transaction.atomic
    def realizar_triaje(ticket_id, area_id, prioridad_id, jefe_area):
        """
        Realiza el triaje inicial del ticket (Nivel 2: Jefe de Área)
        
        Args:
            ticket_id (int): ID del ticket
            area_id (int): ID del área a asignar
            prioridad_id (int): ID de la prioridad
            jefe_area (Usuario): Jefe de área que realiza el triaje
        
        Returns:
            Ticket: El ticket actualizado
        
        Raises:
            ValidationError: Si el usuario no tiene permisos o datos inválidos
        """
        # Validar permisos
        if not jefe_area.puede_asignar_ticket():
            raise ValidationError('El usuario no tiene permisos para realizar triaje')
        
        ticket = Ticket.objects.get(pk=ticket_id)
        
        # Validar que el ticket esté en estado abierto
        if ticket.estado != Ticket.ESTADO_ABIERTO:
            raise ValidationError(f'El ticket debe estar en estado Abierto para realizar triaje. Estado actual: {ticket.estado}')
        
        # Actualizar ticket
        ticket.area_id = area_id
        ticket.prioridad_id = prioridad_id
        ticket.save()
        
        # Registrar en historial
        ticket.registrar_cambio_estado(
            ticket.estado,
            jefe_area,
            f'Triaje realizado. Área: {ticket.area.nombre}, Prioridad: {ticket.prioridad.nombre}'
        )
        
        logger.info(f"Triaje realizado en ticket {ticket.folio} por {jefe_area.nombre}")
        
        return ticket
    
    @staticmethod
    @transaction.atomic
    def asignar_ticket(ticket_id, usuario_asignado_id, jefe_area, motivo=''):
        """
        Asigna un ticket a un usuario operativo (Nivel 2: Jefe de Área)
        
        Args:
            ticket_id (int): ID del ticket
            usuario_asignado_id (int): ID del usuario a asignar
            jefe_area (Usuario): Jefe de área que asigna
            motivo (str): Motivo de la asignación
        
        Returns:
            Ticket: El ticket asignado
        """
        # Validar permisos
        if not jefe_area.puede_asignar_ticket():
            raise ValidationError('El usuario no tiene permisos para asignar tickets')
        
        ticket = Ticket.objects.get(pk=ticket_id)
        
        from apps.usuarios.models import Usuario
        usuario_asignado = Usuario.objects.get(pk=usuario_asignado_id)
        
        # Validar que el ticket tenga área asignada
        if not ticket.area:
            raise ValidationError('El ticket debe tener un área asignada antes de asignarse')
        
        # Asignar usando el método del modelo
        ticket.asignar_a(usuario_asignado, jefe_area, motivo)
        
        logger.info(f"Ticket {ticket.folio} asignado a {usuario_asignado.nombre} por {jefe_area.nombre}")
        
        return ticket
    
    @staticmethod
    @transaction.atomic
    def iniciar_atencion_ticket(ticket_id, usuario_operativo, comentario=''):
        """
        Inicia la atención de un ticket (Nivel 1: Operativo)
        
        Args:
            ticket_id (int): ID del ticket
            usuario_operativo (Usuario): Usuario que inicia la atención
            comentario (str): Comentario adicional
        
        Returns:
            Ticket: El ticket actualizado
        """
        ticket = Ticket.objects.get(pk=ticket_id)
        
        # Validar que el ticket esté asignado al usuario
        if ticket.usuario_asignado != usuario_operativo:
            raise ValidationError('El ticket no está asignado a este usuario')
        
        # Validar estado
        if ticket.estado not in [Ticket.ESTADO_ASIGNADO]:
            raise ValidationError('El ticket debe estar en estado Asignado para iniciar atención')
        
        # Iniciar atención
        ticket.iniciar_atencion(usuario_operativo, comentario)
        
        logger.info(f"Atención iniciada en ticket {ticket.folio} por {usuario_operativo.nombre}")
        
        return ticket
    
    @staticmethod
    @transaction.atomic
    def cerrar_ticket(ticket_id, usuario, comentario=''):
        """
        Cierra un ticket
        
        Args:
            ticket_id (int): ID del ticket
            usuario (Usuario): Usuario que cierra el ticket
            comentario (str): Comentario de cierre
        
        Returns:
            Ticket: El ticket cerrado
        """
        ticket = Ticket.objects.get(pk=ticket_id)
        
        # Validar permisos según nivel jerárquico
        if usuario.es_operativo:
            # Operativo solo puede cerrar tickets asignados a él
            if ticket.usuario_asignado != usuario:
                raise ValidationError('No tiene permisos para cerrar este ticket')
        
        # Cerrar ticket
        ticket.cerrar(usuario, comentario)
        
        logger.info(f"Ticket {ticket.folio} cerrado por {usuario.nombre}")
        
        return ticket
    
    @staticmethod
    def cerrar_tickets_inactivos():
        """
        Cierra automáticamente tickets inactivos
        Este método se ejecutará mediante un comando de management o tarea programada
        
        Returns:
            int: Cantidad de tickets cerrados
        """
        dias_inactividad = settings.TICKET_SETTINGS.get('AUTO_CLOSE_DAYS', 7)
        fecha_limite = timezone.now() - timedelta(days=dias_inactividad)
        
        # Buscar tickets abiertos o asignados sin actividad
        tickets_inactivos = Ticket.objects.filter(
            estado__in=[Ticket.ESTADO_ABIERTO, Ticket.ESTADO_ASIGNADO],
            updated_at__lt=fecha_limite,
            is_active=True
        )
        
        count = 0
        for ticket in tickets_inactivos:
            ticket.cerrar_automaticamente(
                f'Cerrado automáticamente por inactividad de {dias_inactividad} días'
            )
            count += 1
        
        logger.info(f"{count} tickets cerrados automáticamente por inactividad")
        
        return count
    
    @staticmethod
    def obtener_tickets_por_usuario(usuario):
        """
        Obtiene tickets según el nivel jerárquico del usuario
        Pattern: Strategy Pattern
        
        Args:
            usuario (Usuario): Usuario solicitante
        
        Returns:
            QuerySet: Tickets filtrados según permisos
        """
        # Nivel 3: Supervisión General - ve todos los tickets
        if usuario.es_supervision_general:
            return Ticket.objects.filter(is_active=True)
        
        # Nivel 2: Jefe de Área - ve tickets de su área
        if usuario.es_jefe_area:
            area_usuario = usuario.get_area()  # TODO: Implementar lógica de área del usuario
            if area_usuario:
                return Ticket.objects.por_area(area_usuario)
            return Ticket.objects.filter(is_active=True)  # Temporal: ver todos
        
        # Nivel 1: Operativo - solo ve tickets asignados a él
        if usuario.es_operativo:
            return Ticket.objects.por_usuario(usuario)
        
        return Ticket.objects.none()
    
    @staticmethod
    def obtener_proximo_ticket_fifo(area=None):
        """
        Obtiene el próximo ticket a atender según FIFO
        
        Args:
            area (Area): Área específica (opcional)
        
        Returns:
            Ticket: El ticket más antiguo sin atender
        """
        queryset = Ticket.objects.filter(
            estado=Ticket.ESTADO_ABIERTO,
            is_active=True
        ).order_by('fecha_creacion')  # FIFO
        
        if area:
            queryset = queryset.filter(area=area)
        
        return queryset.first()
    
    @staticmethod
    def obtener_estadisticas_sla(area=None, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene estadísticas de cumplimiento de SLA
        
        Args:
            area (Area): Área específica (opcional)
            fecha_inicio (datetime): Fecha de inicio del período
            fecha_fin (datetime): Fecha de fin del período
        
        Returns:
            dict: Estadísticas de SLA
        """
        queryset = Ticket.objects.filter(is_active=True)
        
        if area:
            queryset = queryset.filter(area=area)
        
        if fecha_inicio:
            queryset = queryset.filter(fecha_creacion__gte=fecha_inicio)
        
        if fecha_fin:
            queryset = queryset.filter(fecha_creacion__lte=fecha_fin)
        
        tickets_activos = queryset.exclude(
            estado__in=[Ticket.ESTADO_CERRADO, Ticket.ESTADO_CERRADO_AUTOMATICO]
        )

        total_tickets = tickets_activos.count()

        # Contar por estado de SLA de tickets activos
        verde = 0
        amarillo = 0
        rojo = 0

        for ticket in tickets_activos:
            status = ticket.sla_status
            if status == 'verde':
                verde += 1
            elif status == 'amarillo':
                amarillo += 1
            elif status == 'rojo':
                rojo += 1

        # Cumplimiento real: tickets cerrados dentro del tiempo límite SLA
        tickets_cerrados = queryset.filter(
            estado__in=[Ticket.ESTADO_CERRADO, Ticket.ESTADO_CERRADO_AUTOMATICO],
            fecha_cierre__isnull=False
        )

        total_cerrados = tickets_cerrados.count()
        cerrados_en_tiempo = 0
        for ticket in tickets_cerrados:
            if ticket.tiempo_limite_resolucion and ticket.fecha_cierre <= ticket.tiempo_limite_resolucion:
                cerrados_en_tiempo += 1

        cumplimiento_porcentaje = (cerrados_en_tiempo / total_cerrados * 100) if total_cerrados > 0 else 0
        
        return {
            'total_tickets': total_tickets,
            'sla_verde': verde,
            'sla_amarillo': amarillo,
            'sla_rojo': rojo,
            'verde': verde,
            'amarillo': amarillo,
            'rojo': rojo,
            'total_cerrados': total_cerrados,
            'cerrados_en_tiempo': cerrados_en_tiempo,
            'cumplimiento_porcentaje': round(cumplimiento_porcentaje, 2),
            'cumplimiento': round(cumplimiento_porcentaje, 2),
        }

    @staticmethod
    def obtener_promedios_tiempos(area=None, fecha_inicio=None, fecha_fin=None):
        """Obtiene promedios de primera atención y resolución."""
        queryset = Ticket.objects.filter(is_active=True)

        if area:
            queryset = queryset.filter(area=area)

        if fecha_inicio:
            queryset = queryset.filter(fecha_creacion__gte=fecha_inicio)

        if fecha_fin:
            queryset = queryset.filter(fecha_creacion__lte=fecha_fin)

        tickets_con_atencion = queryset.exclude(fecha_inicio_atencion__isnull=True)
        tickets_cerrados = queryset.exclude(fecha_cierre__isnull=True)

        total_atencion = 0
        count_atencion = 0
        for ticket in tickets_con_atencion:
            minutos = ticket.tiempo_primera_atencion_minutos
            if minutos is not None:
                total_atencion += minutos
                count_atencion += 1

        total_resolucion = 0
        count_resolucion = 0
        for ticket in tickets_cerrados:
            horas = ticket.tiempo_resolucion_horas
            if horas is not None:
                total_resolucion += horas
                count_resolucion += 1

        promedio_primera_atencion = round(total_atencion / count_atencion, 2) if count_atencion else 0
        promedio_resolucion = round(total_resolucion / count_resolucion, 2) if count_resolucion else 0

        return {
            'promedio_primera_atencion_minutos': promedio_primera_atencion,
            'promedio_resolucion_horas': promedio_resolucion,
            'tickets_con_atencion': count_atencion,
            'tickets_cerrados': count_resolucion,
        }

    @staticmethod
    @transaction.atomic
    def liberar_ticket(ticket_id, usuario):
        """
        Libera un ticket cerrándolo por decisión de jefatura.
        Regla de negocio: solo Jefe de Área puede liberar.
        
        Args:
            ticket_id (int): ID del ticket
            usuario (Usuario): Usuario que libera el ticket
            
        Returns:
            Ticket: El ticket liberado
        """
        ticket = Ticket.objects.get(pk=ticket_id)
        
        # Solo Jefe de Área puede liberar
        if not usuario.es_jefe_area:
            raise ValidationError('Solo el jefe de área puede liberar tickets')

        # Jefe solo puede liberar tickets de su propia área
        if usuario.area and ticket.area_id != usuario.area_id:
            raise ValidationError('Solo puede liberar tickets de su área')
        
        # Validar estado
        if ticket.estado not in [Ticket.ESTADO_ASIGNADO, Ticket.ESTADO_EN_ATENCION]:
            raise ValidationError(f'El ticket debe estar Asignado o En Atención. Estado actual: {ticket.estado}')
        
        # Liberar = cerrar por jefatura (no debe quedar como activo)
        ticket.estado = Ticket.ESTADO_CERRADO
        ticket.fecha_cierre = timezone.now()
        ticket.save()

        ticket.registrar_cambio_estado(
            Ticket.ESTADO_CERRADO,
            usuario,
            f'Ticket liberado/cerrado por jefatura: {usuario.nombre}'
        )
        
        logger.info(f"Ticket {ticket.folio} liberado por {usuario.nombre}")
        return ticket

    @staticmethod
    @transaction.atomic
    def retomar_ticket(ticket_id, usuario, motivo=''):
        """
        Retoma un ticket previamente cerrado, reabriéndolo para atención.
        
        Args:
            ticket_id (int): ID del ticket
            usuario (Usuario): Usuario que retoma el ticket
            motivo (str): Motivo del retome
            
        Returns:
            Ticket: El ticket reabierto para continuar trabajo
        """
        ticket = Ticket.objects.get(pk=ticket_id)
        
        # Solo jefatura puede retomar
        if not usuario.es_jefe_area:
            raise ValidationError('Solo el jefe de área puede retomar tickets')

        # Jefe solo puede retomar tickets de su área
        if usuario.area and ticket.area_id != usuario.area_id:
            raise ValidationError('Solo puede retomar tickets de su área')
        
        # Validar estado
        if ticket.estado not in [Ticket.ESTADO_CERRADO, Ticket.ESTADO_CERRADO_AUTOMATICO]:
            raise ValidationError(f'El ticket debe estar Cerrado para retomarlo. Estado actual: {ticket.estado}')
        
        # Reabrir ticket para continuidad
        ticket.estado = Ticket.ESTADO_ASIGNADO if ticket.usuario_asignado else Ticket.ESTADO_ABIERTO
        ticket.fecha_cierre = None
        ticket.save()

        ticket.registrar_cambio_estado(
            ticket.estado,
            usuario,
            f'Ticket retomado por {usuario.nombre}. Motivo: {motivo}'
        )
        
        logger.info(f"Ticket {ticket.folio} retomado por {usuario.nombre}")
        return ticket

    @staticmethod
    @transaction.atomic
    def devolver_ticket(ticket_id, usuario, motivo=''):
        """Alias de compatibilidad para retomar_ticket."""
        return TicketService.retomar_ticket(ticket_id=ticket_id, usuario=usuario, motivo=motivo)
