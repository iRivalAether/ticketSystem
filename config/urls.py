"""
URL configuration for ticketSystem project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Importar vistas
from apps.tickets import views as ticket_views

# API Documentation
schema_view = get_schema_view(
    openapi.Info(
        title="Sistema de Gestión de Tickets API",
        default_version='v1',
        description="""
        API del Sistema de Gestión de Procesos de Soporte (Ticketing)
        
        Características:
        - Gestión de tickets con control de SLA
        - Jerarquía de 3 niveles de usuarios
        - Seguimiento FIFO (First In, First Out)
        - Reportes y KPIs avanzados
        - Control de jornadas (Matutina, Vespertina, Nocturna)
        """,
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="soporte@example.com"),
        license=openapi.License(name="Proprietary"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Autenticación
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # Dashboard
    path('', ticket_views.dashboard, name='dashboard'),
    
    # Tickets
    path('tickets/', ticket_views.ticket_list, name='ticket_list'),
    path('tickets/crear/', ticket_views.ticket_crear, name='ticket_crear'),
    path('tickets/<int:ticket_id>/', ticket_views.ticket_detail, name='ticket_detalle'),
    path('tickets/<int:ticket_id>/atencion/', ticket_views.ticket_atencion, name='ticket_atencion'),
    path('tickets/<int:ticket_id>/cerrar/', ticket_views.ticket_cerrar, name='ticket_cerrar'),
    path('tickets/<int:ticket_id>/liberar/', ticket_views.ticket_liberar, name='ticket_liberar'),
    path('tickets/<int:ticket_id>/devolver/', ticket_views.ticket_devolver, name='ticket_devolver'),
    path('tickets/<int:ticket_id>/retomar/', ticket_views.ticket_retomar, name='ticket_retomar'),
    
    # Triaje
    path('triaje/', ticket_views.ticket_triaje, name='ticket_triaje'),
    path('triaje/<int:ticket_id>/', ticket_views.ticket_realizar_triaje, name='ticket_realizar_triaje'),
    path('configuracion/semaforo-sla/', ticket_views.semaforo_config, name='semaforo_config'),
    
    # Usuarios
    path('usuarios/', include('apps.usuarios.urls')),
    
    # Reportes
    path('reportes/', ticket_views.reportes, name='reportes'),

    # AJAX / Live stats
    path('api/dashboard/stats/', ticket_views.dashboard_stats_api, name='dashboard_stats_api'),
    path('api/reportes/stats/', ticket_views.reportes_stats_api, name='reportes_stats_api'),
    
    # API Documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API Endpoints (pendientes de implementar)
    # path('api/v1/usuarios/', include('apps.usuarios.urls')),
    # path('api/v1/tickets/', include('apps.tickets.urls')),
    # path('api/v1/reportes/', include('apps.reportes.urls')),
    # path('api/v1/core/', include('apps.core.urls')),
]

# Static and Media files
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Debug Toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

# Customize Admin Site
admin.site.site_header = "Sistema de Gestión de Tickets"
admin.site.site_title = "Ticket System Admin"
admin.site.index_title = "Panel de Administración"
