"""
Signals para el módulo de tickets
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Ticket, TicketEstadoHistorial


@receiver(post_save, sender=Ticket)
def ticket_post_save(sender, instance, created, **kwargs):
    """
    Signal que se ejecuta después de guardar un ticket
    """
    if created:
        # Registrar el primer estado (Abierto) en el historial
        TicketEstadoHistorial.objects.create(
            ticket=instance,
            estado=instance.estado,
            usuario=None,
            comentario='Ticket creado'
        )


@receiver(pre_save, sender=Ticket)
def ticket_pre_save(sender, instance, **kwargs):
    """
    Signal que se ejecuta antes de guardar un ticket
    Útil para validaciones y lógica de negocio
    """
    # Si el ticket está siendo cerrado, asegurar que tenga fecha de cierre
    if instance.pk:
        try:
            old_instance = Ticket.objects.get(pk=instance.pk)
            # Detectar cambio a estado cerrado
            if old_instance.estado != instance.estado:
                if instance.estado in [Ticket.ESTADO_CERRADO, Ticket.ESTADO_CERRADO_AUTOMATICO]:
                    if not instance.fecha_cierre:
                        from django.utils import timezone
                        instance.fecha_cierre = timezone.now()
        except Ticket.DoesNotExist:
            pass
