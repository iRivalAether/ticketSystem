"""
Template tags personalizados para timestamps relativos e ISO.
"""
from django import template
from django.utils import timezone
from datetime import datetime, timedelta

register = template.Library()


@register.filter
def time_since_human(dt):
    """
    Convierte un datetime a formato legible: "hace 5 segundos", "hace 2 minutos", etc.
    
    Ejemplos:
        {{ ticket.updated_at|time_since_human }}  →  "hace 5 segundos"
        {{ ticket.created_at|time_since_human }}   →  "hace 2 horas"
    """
    if not dt:
        return ""
    
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except:
            return dt
    
    # Asegurar que ambos son timezone-aware
    now = timezone.now()
    if dt.tzinfo is None:
        dt = timezone.make_aware(dt)
    
    delta = now - dt
    
    # Segundos
    if delta < timedelta(seconds=60):
        seconds = int(delta.total_seconds())
        return f"hace {seconds} segundo{'s' if seconds != 1 else ''}"
    
    # Minutos
    if delta < timedelta(minutes=60):
        minutes = int(delta.total_seconds() / 60)
        return f"hace {minutes} minuto{'s' if minutes != 1 else ''}"
    
    # Horas
    if delta < timedelta(hours=24):
        hours = int(delta.total_seconds() / 3600)
        return f"hace {hours} hora{'s' if hours != 1 else ''}"
    
    # Días
    if delta < timedelta(days=7):
        days = int(delta.total_seconds() / 86400)
        return f"hace {days} día{'s' if days != 1 else ''}"
    
    # Semanas
    if delta < timedelta(days=30):
        weeks = int(delta.total_seconds() / 604800)
        return f"hace {weeks} semana{'s' if weeks != 1 else ''}"
    
    # Meses (aproximado)
    if delta < timedelta(days=365):
        months = int(delta.total_seconds() / 2592000)
        return f"hace {months} mes{'es' if months != 1 else ''}"
    
    # Años
    years = int(delta.total_seconds() / 31536000)
    return f"hace {years} año{'s' if years != 1 else ''}"


@register.filter
def timestamp_iso(dt):
    """
    Convierte un datetime a ISO format para usar en atributos data-*.
    
    Ejemplos:
        {{ ticket.updated_at|timestamp_iso }}  →  "2026-03-24T14:30:45.123456+00:00"
    """
    if not dt:
        return ""
    
    if isinstance(dt, str):
        return dt
    
    if isinstance(dt, datetime):
        return dt.isoformat()
    
    return ""


@register.filter
def timestamp_readable(dt):
    """
    Convierte datetime a formato legible: "24 de marzo, 14:30"
    """
    if not dt:
        return ""
    
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except:
            return dt
    
    return dt.strftime("%d de %B, %H:%M")


@register.filter(name="add_class")
def add_class(field, css_classes):
    """Append CSS classes to a Django form field widget."""
    existing_classes = field.field.widget.attrs.get("class", "")
    combined_classes = f"{existing_classes} {css_classes}".strip()
    return field.as_widget(attrs={"class": combined_classes})
