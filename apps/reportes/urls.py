"""
URLs para el módulo de Reportes
"""
from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('csv/', views.descargar_reporte_csv, name='reportes_export_csv'),
]
