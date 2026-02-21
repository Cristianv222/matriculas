"""
URLs principales del proyecto SFQ MatrÃ­culas
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = 'SFQ MatrÃ­culas - AdministraciÃ³n'
admin.site.site_title = 'San Francisco de Quito'
admin.site.index_title = 'Panel de AdministraciÃ³n'

urlpatterns = [
    # Admin Django
    path('admin/', admin.site.urls),

    # MÃ³dulos de la aplicaciÃ³n
    path('', include('apps.core.urls', namespace='core')),
    path('usuarios/', include('apps.usuarios.urls', namespace='usuarios')),
    path('estudiantes/', include('apps.estudiantes.urls', namespace='estudiantes')),
    path('periodos/', include('apps.periodos.urls', namespace='periodos')),
    path('matriculas/', include('apps.matriculas.urls', namespace='matriculas')),
    path('documentos/', include('apps.documentos.urls', namespace='documentos')),
    path('notificaciones/', include('apps.notificaciones.urls', namespace='notificaciones')),
    path('reportes/', include('apps.reportes.urls', namespace='reportes')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
