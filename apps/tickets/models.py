"""
Modelos del sistema de Tickets

Implementa:
- Gestión de tickets con estados y SLA
- Historial de estados y asignaciones
- Control de prioridades y áreas
- Sistema de jornadas (Matutina, Vespertina, Nocturna)
- FIFO (First In, First Out)
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta, time as time_cls
from apps.core.models import BaseModel


class Jornada(BaseModel):
    """
    Modelo de Jornada laboral
    Basado en tabla 'jornada' del diagrama
    """
    MATUTINA = 'Matutina'
    VESPERTINA = 'Vespertina'
    NOCTURNA = 'Nocturna'
    
    TIPOS_JORNADA = [
        (MATUTINA, 'Matutina'),
        (VESPERTINA, 'Vespertina'),
        (NOCTURNA, 'Nocturna'),
    ]
    
    nombre = models.CharField(
        'Nombre de la jornada',
        max_length=100,
        choices=TIPOS_JORNADA,
        unique=True
    )

    HORARIOS_POR_JORNADA = {
        MATUTINA: [(6, 14)],
        VESPERTINA: [(14, 22)],
        NOCTURNA: [(22, 24), (0, 6)],
    }
    
    class Meta:
        db_table = 'jornada'
        verbose_name = 'Jornada'
        verbose_name_plural = 'Jornadas'
        ordering = ['id']
    
    def __str__(self):
        return self.nombre

    def get_intervalos_horarios(self):
        """Retorna los intervalos horarios activos de la jornada."""
        return self.HORARIOS_POR_JORNADA.get(self.nombre, [(0, 24)])


class Area(BaseModel):
    """
    Modelo de Área de atención
    Basado en tabla 'area' del diagrama
    """
    nombre = models.CharField(
        'Nombre del área',
        max_length=100,
        unique=True
    )
    
    class Meta:
        db_table = 'area'
        verbose_name = 'Área'
        verbose_name_plural = 'Áreas'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Prioridad(BaseModel):
    """
    Modelo de Prioridad de tickets
    Basado en tabla 'prioridad' del diagrama
    """
    nombre = models.CharField(
        'Nombre de la prioridad',
        max_length=50,
        unique=True
    )
    nivel = models.IntegerField(
        'Nivel de prioridad',
        help_text='Menor número = Mayor prioridad',
        default=3
    )
    
    class Meta:
        db_table = 'prioridad'
        verbose_name = 'Prioridad'
        verbose_name_plural = 'Prioridades'
        ordering = ['nivel']
    
    def __str__(self):
        return f"{self.nombre} (Nivel {self.nivel})"


class SLA(BaseModel):
    """
    Modelo de SLA (Service Level Agreement)
    Basado en tabla 'sla' del diagrama
    """
    nombre = models.CharField(
        'Nombre del SLA',
        max_length=100,
        unique=True
    )
    tiempo_respuesta = models.IntegerField(
        'Tiempo de respuesta (minutos)',
        help_text='Tiempo máximo para primera respuesta'
    )
    tiempo_resolucion = models.FloatField(
        'Tiempo de resolución (horas)',
        help_text='Tiempo máximo para resolución completa'
    )
    
    class Meta:
        db_table = 'sla'
        verbose_name = 'SLA'
        verbose_name_plural = 'SLAs'
        ordering = ['tiempo_resolucion']
    
    def __str__(self):
        return f"{self.nombre} (Respuesta: {self.tiempo_respuesta}min, Resolución: {self.tiempo_resolucion}h)"
    
    def get_tiempo_resolucion_timedelta(self):
        """Retorna el tiempo de resolución como timedelta"""
        return timedelta(hours=self.tiempo_resolucion)
    
    def get_tiempo_respuesta_timedelta(self):
        """Retorna el tiempo de respuesta como timedelta"""
        return timedelta(minutes=self.tiempo_respuesta)


class SemaforoSLAConfig(BaseModel):
    """Configuración dinámica de umbrales del semáforo SLA."""
    nombre = models.CharField(
        'Nombre de la configuración',
        max_length=100,
        default='Configuración Global',
        unique=True
    )
    warning_percentage = models.PositiveIntegerField(
        'Porcentaje de alerta (amarillo)',
        default=80,
        help_text='Al llegar a este porcentaje del tiempo SLA, cambia a amarillo.'
    )
    danger_percentage = models.PositiveIntegerField(
        'Porcentaje crítico (rojo)',
        default=100,
        help_text='Al llegar a este porcentaje del tiempo SLA, cambia a rojo.'
    )

    class Meta:
        db_table = 'semaforo_sla_config'
        verbose_name = 'Configuración de Semáforo SLA'
        verbose_name_plural = 'Configuración de Semáforo SLA'

    def __str__(self):
        return f"{self.nombre} ({self.warning_percentage}%/{self.danger_percentage}%)"

    @classmethod
    def get_default_config(cls):
        config, _ = cls.objects.get_or_create(
            nombre='Configuración Global',
            defaults={
                'warning_percentage': settings.TICKET_SETTINGS.get('SLA_WARNING_PERCENTAGE', 80),
                'danger_percentage': settings.TICKET_SETTINGS.get('SLA_DANGER_PERCENTAGE', 100),
            }
        )
        return config


class TicketManager(models.Manager):
    """
    Manager personalizado para Ticket
    Pattern: Repository Pattern
    """
    def abiertos(self):
        """Retorna tickets abiertos"""
        return self.filter(estado='Abierto', is_active=True)
    
    def asignados(self):
        """Retorna tickets asignados"""
        return self.filter(estado='Asignado', is_active=True)
    
    def en_atencion(self):
        """Retorna tickets en atención"""
        return self.filter(estado='En Atención', is_active=True)
    
    def cerrados(self):
        """Retorna tickets cerrados"""
        return self.filter(estado__in=['Cerrado', 'Cerrado Automático'], is_active=True)
    
    def por_area(self, area):
        """Retorna tickets de un área específica"""
        return self.filter(area=area, is_active=True)
    
    def por_jornada(self, jornada):
        """Retorna tickets de una jornada específica"""
        return self.filter(jornada=jornada, is_active=True)
    
    def por_usuario(self, usuario):
        """Retorna tickets asignados a un usuario"""
        return self.filter(usuario_asignado=usuario, is_active=True)
    
    def sla_vencido(self):
        """Retorna tickets con SLA vencido (semáforo rojo)"""
        now = timezone.now()
        tickets = []
        for ticket in self.exclude(estado__in=['Cerrado', 'Cerrado Automático']).filter(is_active=True):
            if ticket.sla_status == 'rojo':
                tickets.append(ticket.pk)
        return self.filter(pk__in=tickets)
    
    def sla_proximo_vencer(self):
        """Retorna tickets con SLA próximo a vencer (semáforo amarillo)"""
        now = timezone.now()
        tickets = []
        for ticket in self.exclude(estado__in=['Cerrado', 'Cerrado Automático']).filter(is_active=True):
            if ticket.sla_status == 'amarillo':
                tickets.append(ticket.pk)
        return self.filter(pk__in=tickets)


class Ticket(BaseModel):
    """
    Modelo principal de Ticket
    Basado en tabla 'ticket' del diagrama
    
    Implementa FIFO (First In, First Out) mediante ordenamiento por fecha de creación
    """
    ESTADO_ABIERTO = 'Abierto'
    ESTADO_ASIGNADO = 'Asignado'
    ESTADO_EN_ATENCION = 'En Atención'
    ESTADO_CERRADO = 'Cerrado'
    ESTADO_CERRADO_AUTOMATICO = 'Cerrado Automático'
    
    ESTADOS = [
        (ESTADO_ABIERTO, 'Abierto'),
        (ESTADO_ASIGNADO, 'Asignado'),
        (ESTADO_EN_ATENCION, 'En Atención'),
        (ESTADO_CERRADO, 'Cerrado'),
        (ESTADO_CERRADO_AUTOMATICO, 'Cerrado Automático'),
    ]
    
    # Campos principales
    nombre = models.CharField(
        'Título del ticket',
        max_length=255
    )
    descripcion = models.TextField(
        'Descripción',
        blank=True
    )
    estado = models.CharField(
        'Estado',
        max_length=20,
        choices=ESTADOS,
        default=ESTADO_ABIERTO,
        db_index=True
    )
    fecha_creacion = models.DateTimeField(
        'Fecha de creación',
        auto_now_add=True,
        db_index=True
    )
    fecha_cierre = models.DateTimeField(
        'Fecha de cierre',
        null=True,
        blank=True
    )
    
    # Relaciones
    area = models.ForeignKey(
        Area,
        on_delete=models.PROTECT,
        related_name='tickets',
        verbose_name='Área',
        null=True,
        blank=True
    )
    usuario_asignado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='tickets_asignados',
        verbose_name='Usuario asignado',
        null=True,
        blank=True
    )
    prioridad = models.ForeignKey(
        Prioridad,
        on_delete=models.PROTECT,
        related_name='tickets',
        verbose_name='Prioridad'
    )
    sla = models.ForeignKey(
        SLA,
        on_delete=models.PROTECT,
        related_name='tickets',
        verbose_name='SLA'
    )
    jornada = models.ForeignKey(
        Jornada,
        on_delete=models.PROTECT,
        related_name='tickets',
        verbose_name='Jornada'
    )
    
    # Control de tiempo
    fecha_inicio_atencion = models.DateTimeField(
        'Fecha inicio de atención',
        null=True,
        blank=True
    )
    
    objects = TicketManager()
    
    class Meta:
        db_table = 'ticket'
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        ordering = ['fecha_creacion']  # FIFO: First In, First Out
        indexes = [
            models.Index(fields=['estado', 'fecha_creacion']),
            models.Index(fields=['area', 'estado']),
            models.Index(fields=['usuario_asignado', 'estado']),
        ]
    
    def __str__(self):
        return f"#{self.pk} - {self.nombre}"

    @staticmethod
    def _asegurar_aware(fecha):
        """Normaliza una fecha a timezone aware en la zona local."""
        if fecha is None:
            return None
        if timezone.is_naive(fecha):
            return timezone.make_aware(fecha, timezone.get_current_timezone())
        return timezone.localtime(fecha)

    def _obtener_intervalos_jornada(self):
        """Devuelve los intervalos de trabajo aplicables al ticket."""
        if self.jornada:
            return self.jornada.get_intervalos_horarios()
        return [(0, 24)]

    def _calcular_tiempo_habil_entre(self, inicio, fin):
        """Calcula el tiempo transcurrido solo dentro de la jornada."""
        inicio = self._asegurar_aware(inicio)
        fin = self._asegurar_aware(fin)

        if not inicio or not fin or fin <= inicio:
            return timedelta(0)

        total = timedelta(0)
        fecha_actual = inicio.date()
        fecha_fin = fin.date()
        intervalos = self._obtener_intervalos_jornada()
        zona_horaria = timezone.get_current_timezone()

        while fecha_actual <= fecha_fin:
            for hora_inicio, hora_fin in intervalos:
                inicio_intervalo = datetime.combine(fecha_actual, time_cls(hour=hora_inicio, minute=0))
                if hora_fin == 24:
                    fin_intervalo = datetime.combine(fecha_actual + timedelta(days=1), time_cls(hour=0, minute=0))
                else:
                    fin_intervalo = datetime.combine(fecha_actual, time_cls(hour=hora_fin, minute=0))

                inicio_intervalo = timezone.make_aware(inicio_intervalo, zona_horaria)
                fin_intervalo = timezone.make_aware(fin_intervalo, zona_horaria)

                interseccion_inicio = max(inicio, inicio_intervalo)
                interseccion_fin = min(fin, fin_intervalo)

                if interseccion_fin > interseccion_inicio:
                    total += interseccion_fin - interseccion_inicio

            fecha_actual += timedelta(days=1)

        return total

    def _sumar_tiempo_habil(self, inicio, duracion):
        """Suma una duración respetando las ventanas de la jornada."""
        inicio = self._asegurar_aware(inicio)
        if not inicio or duracion is None:
            return inicio

        restante = duracion
        cursor = inicio
        zona_horaria = timezone.get_current_timezone()

        while restante > timedelta(0):
            intervalos = self._obtener_intervalos_jornada()
            avanzando = False

            for hora_inicio, hora_fin in intervalos:
                inicio_intervalo = datetime.combine(cursor.date(), time_cls(hour=hora_inicio, minute=0))
                if hora_fin == 24:
                    fin_intervalo = datetime.combine(cursor.date() + timedelta(days=1), time_cls(hour=0, minute=0))
                else:
                    fin_intervalo = datetime.combine(cursor.date(), time_cls(hour=hora_fin, minute=0))

                inicio_intervalo = timezone.make_aware(inicio_intervalo, zona_horaria)
                fin_intervalo = timezone.make_aware(fin_intervalo, zona_horaria)

                if cursor >= fin_intervalo:
                    continue

                inicio_efectivo = max(cursor, inicio_intervalo)
                disponible = fin_intervalo - inicio_efectivo

                if disponible <= timedelta(0):
                    continue

                if restante <= disponible:
                    return inicio_efectivo + restante

                restante -= disponible
                cursor = fin_intervalo
                avanzando = True

            if not avanzando:
                siguiente_dia = cursor.date() + timedelta(days=1)
                cursor = timezone.make_aware(
                    datetime.combine(siguiente_dia, time_cls(hour=0, minute=0)),
                    zona_horaria
                )

        return cursor
    
    @property
    def folio(self):
        """
        Genera un folio único e inalterable para el ticket
        Formato: TKT-{ID:06d}
        """
        prefix = settings.TICKET_SETTINGS.get('FOLIO_PREFIX', 'TKT')
        return f"{prefix}-{self.pk:06d}"
    
    @property
    def tiempo_transcurrido(self):
        """Calcula el tiempo transcurrido desde la creación"""
        referencia = self.fecha_cierre if self.estado in [self.ESTADO_CERRADO, self.ESTADO_CERRADO_AUTOMATICO] and self.fecha_cierre else timezone.now()
        return self._calcular_tiempo_habil_entre(self.fecha_creacion, referencia)
    
    @property
    def tiempo_limite_resolucion(self):
        """Calcula el tiempo límite para resolución según SLA"""
        if self.sla:
            return self._sumar_tiempo_habil(self.fecha_creacion, self.sla.get_tiempo_resolucion_timedelta())
        return None
    
    @property
    def sla_status(self):
        """
        Retorna el estado del SLA (semáforo)
        - 'verde': Dentro de tiempo
        - 'amarillo': Próximo a vencer (>80% del tiempo)
        - 'rojo': SLA vencido (>100% del tiempo)
        """
        if self.estado in [self.ESTADO_CERRADO, self.ESTADO_CERRADO_AUTOMATICO]:
            if self.fecha_cierre and self.tiempo_limite_resolucion:
                return 'verde' if self.fecha_cierre <= self.tiempo_limite_resolucion else 'rojo'
            return 'verde'  # Ticket cerrado
        
        if not self.tiempo_limite_resolucion:
            return 'verde'
        
        tiempo_total = self.sla.get_tiempo_resolucion_timedelta()

        tiempo_usado = self._calcular_tiempo_habil_entre(self.fecha_creacion, timezone.now())
        porcentaje_usado = (tiempo_usado / tiempo_total) * 100 if tiempo_total.total_seconds() else 0
        
        config = SemaforoSLAConfig.get_default_config()
        sla_warning = config.warning_percentage
        sla_danger = config.danger_percentage
        
        if porcentaje_usado >= sla_danger:
            return 'rojo'
        elif porcentaje_usado >= sla_warning:
            return 'amarillo'
        else:
            return 'verde'

    @property
    def tiempo_primera_atencion_minutos(self):
        """Minutos desde creación hasta inicio de atención."""
        if not self.fecha_inicio_atencion:
            return None
        delta = self.fecha_inicio_atencion - self.fecha_creacion
        return round(delta.total_seconds() / 60, 2)

    @property
    def tiempo_resolucion_horas(self):
        """Horas desde creación hasta cierre."""
        if not self.fecha_cierre:
            return None
        delta = self.fecha_cierre - self.fecha_creacion
        return round(delta.total_seconds() / 3600, 2)
    
    @property
    def puede_cerrarse(self):
        """Determina si el ticket puede cerrarse"""
        return self.estado not in [self.ESTADO_CERRADO, self.ESTADO_CERRADO_AUTOMATICO]
    
    def asignar_a(self, usuario, asignado_por, motivo=''):
        """
        Asigna el ticket a un usuario
        Pattern: Command Pattern
        """
        self.usuario_asignado = usuario
        self.estado = self.ESTADO_ASIGNADO
        self.save()
        
        # Registrar en historial de asignación
        TicketAsignacionHistorial.objects.create(
            ticket=self,
            asignado_a_usuario=usuario,
            asignado_por_usuario=asignado_por,
            motivo=motivo
        )
        
        # Registrar cambio de estado
        self.registrar_cambio_estado(self.ESTADO_ASIGNADO, asignado_por, f'Asignado a {usuario.nombre}')
    
    def iniciar_atencion(self, usuario, comentario=''):
        """Marca el ticket como en atención"""
        self.estado = self.ESTADO_EN_ATENCION
        self.fecha_inicio_atencion = timezone.now()
        self.save()
        
        self.registrar_cambio_estado(self.ESTADO_EN_ATENCION, usuario, comentario)
    
    def cerrar(self, usuario, comentario=''):
        """Cierra el ticket"""
        if self.puede_cerrarse:
            self.estado = self.ESTADO_CERRADO
            self.fecha_cierre = timezone.now()
            self.save()
            
            self.registrar_cambio_estado(self.ESTADO_CERRADO, usuario, comentario)
    
    def cerrar_automaticamente(self, comentario='Cerrado por inactividad'):
        """Cierra el ticket automáticamente"""
        if self.puede_cerrarse:
            self.estado = self.ESTADO_CERRADO_AUTOMATICO
            self.fecha_cierre = timezone.now()
            self.save()
            
            self.registrar_cambio_estado(self.ESTADO_CERRADO_AUTOMATICO, None, comentario)
    
    def registrar_cambio_estado(self, nuevo_estado, usuario, comentario=''):
        """Registra un cambio de estado en el historial"""
        TicketEstadoHistorial.objects.create(
            ticket=self,
            estado=nuevo_estado,
            usuario=usuario,
            comentario=comentario
        )


class TicketEstadoHistorial(BaseModel):
    """
    Historial de cambios de estado de tickets
    Basado en tabla 'ticket_estado_historial' del diagrama
    
    Proporciona trazabilidad completa del ciclo de vida del ticket
    """
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='historial_estados',
        verbose_name='Ticket'
    )
    estado = models.CharField(
        'Estado',
        max_length=20,
        choices=Ticket.ESTADOS
    )
    fecha = models.DateTimeField(
        'Fecha del cambio',
        auto_now_add=True,
        db_index=True
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='cambios_estado_realizados',
        verbose_name='Usuario',
        null=True,
        blank=True
    )
    comentario = models.CharField(
        'Comentario',
        max_length=255,
        blank=True
    )
    
    class Meta:
        db_table = 'ticket_estado_historial'
        verbose_name = 'Historial de Estado'
        verbose_name_plural = 'Historial de Estados'
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['ticket', '-fecha']),
        ]
    
    def __str__(self):
        return f"{self.ticket.folio} - {self.estado} ({self.fecha})"


class TicketAsignacionHistorial(BaseModel):
    """
    Historial de asignaciones de tickets
    Basado en tabla 'ticket_asignacion_historial' del diagrama
    
    Registra todos los cambios de asignación para auditoría
    """
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='historial_asignaciones',
        verbose_name='Ticket'
    )
    asignado_a_usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='asignaciones_recibidas',
        verbose_name='Asignado a',
        null=True
    )
    asignado_por_usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='asignaciones_realizadas',
        verbose_name='Asignado por',
        null=True
    )
    fecha_asignacion = models.DateTimeField(
        'Fecha de asignación',
        auto_now_add=True,
        db_index=True
    )
    motivo = models.CharField(
        'Motivo',
        max_length=255,
        blank=True
    )
    
    class Meta:
        db_table = 'ticket_asignacion_historial'
        verbose_name = 'Historial de Asignación'
        verbose_name_plural = 'Historial de Asignaciones'
        ordering = ['-fecha_asignacion']
        indexes = [
            models.Index(fields=['ticket', '-fecha_asignacion']),
            models.Index(fields=['asignado_a_usuario', '-fecha_asignacion']),
        ]
    
    def __str__(self):
        return f"{self.ticket.folio} - Asignado a {self.asignado_a_usuario}"
