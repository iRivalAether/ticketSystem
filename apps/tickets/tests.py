from datetime import datetime

from django.test import SimpleTestCase
from django.utils import timezone

from apps.tickets.models import Jornada, SLA, Ticket


class TicketSLAJornadaTest(SimpleTestCase):
    """Pruebas unitarias para el cálculo de SLA con ajuste por jornada."""

    def test_tiempo_limite_resolucion_respeta_horario_jornada(self):
        """
        Si el ticket se crea al final de la jornada, el tiempo faltante
        debe continuar al inicio de la siguiente jornada activa.
        """
        jornada = Jornada(nombre=Jornada.MATUTINA)
        sla = SLA(nombre='SLA Test', tiempo_respuesta=30, tiempo_resolucion=2)

        fecha_creacion = timezone.make_aware(datetime(2026, 1, 10, 13, 0, 0), timezone.get_current_timezone())

        ticket = Ticket(
            nombre='Prueba SLA jornada',
            descripcion='Validar cálculo de tiempo hábil',
            jornada=jornada,
            sla=sla,
            fecha_creacion=fecha_creacion,
            estado=Ticket.ESTADO_ABIERTO,
        )

        tiempo_limite = ticket.tiempo_limite_resolucion
        esperado = timezone.make_aware(datetime(2026, 1, 11, 7, 0, 0), timezone.get_current_timezone())

        self.assertEqual(tiempo_limite, esperado)
