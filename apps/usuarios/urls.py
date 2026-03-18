"""
URLs para el módulo de Usuarios
"""
from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Gestión de usuarios
    path('listar/', views.usuario_listar, name='usuario_listar'),
    path('crear/', views.usuario_crear, name='usuario_crear'),
    path('<int:usuario_id>/editar/', views.usuario_editar, name='usuario_editar'),
    path('<int:usuario_id>/detalle/', views.usuario_detalle, name='usuario_detalle'),
]
