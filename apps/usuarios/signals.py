"""
Signals para el módulo de usuarios
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

Usuario = get_user_model()


@receiver(post_save, sender=Usuario)
def usuario_post_save(sender, instance, created, **kwargs):
    """
    Signal que se ejecuta después de guardar un usuario
    """
    if created:
        # Aquí se pueden ejecutar acciones al crear un usuario
        # Por ejemplo: enviar email de bienvenida, crear configuraciones, etc.
        pass
