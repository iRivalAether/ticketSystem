"""
Formularios para gestión de usuarios
"""
from django import forms
from django.contrib.auth.models import User
from apps.usuarios.models import Usuario, Rol
from apps.tickets.models import Area


class UsuarioCrearForm(forms.Form):
    """Formulario para crear nuevos usuarios (solo Supervisores)"""
    
    email = forms.EmailField(
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'usuario@example.com'
        })
    )
    
    nombre = forms.CharField(
        label='Nombre Completo',
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Juan Pérez'
        })
    )
    
    rol = forms.ModelChoiceField(
        label='Rol',
        queryset=Rol.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        help_text='Seleccione el rol jerárquico del usuario'
    )
    
    area = forms.ModelChoiceField(
        label='Área (opcional)',
        queryset=Area.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        required=False,
        help_text='Requerido si el rol es Operativo o Jefe'
    )
    
    password = forms.CharField(
        label='Contraseña Inicial',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña temporal'
        }),
        min_length=8,
        help_text='Mínimo 8 caracteres'
    )
    
    password_confirm = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme la contraseña'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        rol = cleaned_data.get('rol')
        area = cleaned_data.get('area')
        
        # Validar que el email no exista
        if email and User.objects.filter(username=email).exists():
            self.add_error('email', 'Este correo ya está registrado en el sistema')
        
        # Validar que las contraseñas coincidan
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'Las contraseñas no coinciden')
        
        # Validar que operativos y jefes tengan área
        if rol and rol.nivel_jerarquico in [1, 2]:  # Operativo o Jefe
            if not area:
                self.add_error('area', f'El área es requerida para {rol.nombre}')
        
        return cleaned_data


class UsuarioEditarForm(forms.ModelForm):
    """Formulario para editar usuarios (solo Supervisores)"""
    
    rol = forms.ModelChoiceField(
        label='Rol',
        queryset=Rol.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    area = forms.ModelChoiceField(
        label='Área (opcional)',
        queryset=Area.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        required=False
    )
    
    class Meta:
        model = Usuario
        fields = ['nombre', 'rol', 'area', 'is_active']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def clean(self):
        cleaned_data = super().clean()
        rol = cleaned_data.get('rol')
        area = cleaned_data.get('area')
        
        # Validar que operativos y jefes tengan área
        if rol and rol.nivel_jerarquico in [1, 2]:  # Operativo o Jefe
            if not area:
                self.add_error('area', f'El área es requerida para {rol.nombre}')
        
        return cleaned_data
