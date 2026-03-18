from django import forms
from apps.tickets.models import Ticket, Prioridad, Area, SemaforoSLAConfig
from apps.usuarios.models import Usuario


class TicketCreateForm(forms.ModelForm):
    """Formulario para crear tickets (Nivel 1 - Operativos)"""
    
    class Meta:
        model = Ticket
        fields = ['nombre', 'descripcion', 'prioridad']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Error en el sistema de facturación'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describa detalladamente el problema...',
                'rows': 6
            }),
            'prioridad': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'nombre': 'Título del Ticket',
            'descripcion': 'Descripción',
            'prioridad': 'Prioridad'
        }


class TicketTriajeForm(forms.Form):
    """Formulario para realizar triaje (Nivel 2 - Jefes de Área)"""
    
    area = forms.ModelChoiceField(
        queryset=Area.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Área de Asignación'
    )
    
    usuario_asignado = forms.ModelChoiceField(
        queryset=Usuario.objects.none(),  # Se carga dinámicamente
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Asignar a Usuario',
        required=False
    )
    
    comentario = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Comentarios sobre la asignación (opcional)'
        }),
        required=False,
        label='Comentarios'
    )
    
    def __init__(self, *args, **kwargs):
        jefe_area = kwargs.pop('jefe_area', None)
        super().__init__(*args, **kwargs)

        self.fields['usuario_asignado'].queryset = Usuario.objects.filter(
            rol__nivel_jerarquico=1,
            is_active=True
        )

        if jefe_area and jefe_area.es_jefe_area and jefe_area.area:
            self.fields['area'].queryset = Area.objects.filter(id=jefe_area.area_id, is_active=True)

        area_id = self.data.get('area') or self.initial.get('area')
        if area_id:
            self.fields['usuario_asignado'].queryset = Usuario.objects.filter(
                rol__nivel_jerarquico=1,
                area_id=area_id,
                is_active=True
            )


class SemaforoSLAConfigForm(forms.ModelForm):
    """Formulario de configuración de semáforo SLA."""

    class Meta:
        model = SemaforoSLAConfig
        fields = ['warning_percentage', 'danger_percentage']
        widgets = {
            'warning_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 99
            }),
            'danger_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 50,
                'max': 200
            }),
        }
        labels = {
            'warning_percentage': 'Umbral Amarillo (%)',
            'danger_percentage': 'Umbral Rojo (%)',
        }

    def clean(self):
        cleaned_data = super().clean()
        warning = cleaned_data.get('warning_percentage')
        danger = cleaned_data.get('danger_percentage')

        if warning is not None and danger is not None and warning >= danger:
            raise forms.ValidationError('El umbral amarillo debe ser menor que el umbral rojo.')

        return cleaned_data


class TicketCerrarForm(forms.Form):
    """Formulario para cerrar un ticket"""
    
    solucion = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Describa la solución aplicada...'
        }),
        label='Solución Aplicada',
        required=True
    )
    
    comentario = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Comentarios adicionales (opcional)'
        }),
        required=False,
        label='Comentarios Adicionales'
    )
