"""
Modelos base y abstractos del sistema
"""
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Modelo abstracto que proporciona campos de auditoría de tiempo
    Pattern: Base Model / Template Method
    """
    created_at = models.DateTimeField(
        'Fecha de creación',
        auto_now_add=True,
        db_index=True
    )
    updated_at = models.DateTimeField(
        'Fecha de actualización',
        auto_now=True
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']


class SoftDeleteModel(models.Model):
    """
    Modelo abstracto que implementa borrado lógico
    Pattern: Soft Delete
    """
    is_active = models.BooleanField(
        'Activo',
        default=True,
        db_index=True
    )
    deleted_at = models.DateTimeField(
        'Fecha de eliminación',
        null=True,
        blank=True
    )

    class Meta:
        abstract = True

    def soft_delete(self):
        """Marca el registro como eliminado sin borrarlo físicamente"""
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        """Restaura un registro eliminado lógicamente"""
        self.is_active = True
        self.deleted_at = None
        self.save()


class BaseModel(TimeStampedModel, SoftDeleteModel):
    """
    Modelo base que combina timestamp y soft delete
    Pattern: Composite / Template Method
    """
    class Meta:
        abstract = True
