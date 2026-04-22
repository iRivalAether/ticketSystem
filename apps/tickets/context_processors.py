"""
Context processors del módulo de tickets.
"""
from apps.tickets.models import Ticket
from services.ticket_service import TicketService


def sla_alertas(request):
    """Expone alertas visuales de SLA vencido en todo el sitio."""
    if not request.user.is_authenticated:
        return {'sla_alertas_vencidas': 0}

    tickets = TicketService.obtener_tickets_por_usuario(request.user).exclude(
        estado__in=[Ticket.ESTADO_CERRADO, Ticket.ESTADO_CERRADO_AUTOMATICO]
    )
    vencidos = sum(1 for ticket in tickets if ticket.sla_status == 'rojo')

    return {
        'sla_alertas_vencidas': vencidos,
    }