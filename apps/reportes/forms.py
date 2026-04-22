"""
Formularios del módulo de reportes.
"""
from django import forms
from .models import RetroalimentacionTicket


class RetroalimentacionTicketForm(forms.ModelForm):
    """Formulario para registrar retroalimentación por ticket."""

    class Meta:
        model = RetroalimentacionTicket
        fields = ['especialidad', 'calificacion', 'comentario']
        widgets = {
            'especialidad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Soporte, Infraestructura, Seguridad'
            }),
            'calificacion': forms.Select(attrs={
                'class': 'form-control'
            }),
            'comentario': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Observaciones sobre la atención recibida...'
            }),
        }
        labels = {
            'especialidad': 'Especialidad',
            'calificacion': 'Calificación',
            'comentario': 'Comentarios',
        }