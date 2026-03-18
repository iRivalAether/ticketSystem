"""
Comando para cerrar automáticamente tickets inactivos

Uso:
    python manage.py cerrar_tickets_inactivos
"""
from django.core.management.base import BaseCommand
from services.ticket_service import TicketService


class Command(BaseCommand):
    help = 'Cierra automáticamente tickets inactivos según configuración'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando cierre automático de tickets inactivos...')
        
        count = TicketService.cerrar_tickets_inactivos()
        
        self.stdout.write(
            self.style.SUCCESS(f'Se cerraron {count} tickets inactivos exitosamente')
        )
