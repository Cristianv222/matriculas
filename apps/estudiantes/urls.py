"""
============================================================
  MÓDULO: estudiantes — urls.py
============================================================
"""
from django.urls import path, include
from . import views

app_name = 'estudiantes'

# ── Vistas web ────────────────────────────────────────────────────────────────
web_urlpatterns = [
    path('',              views.EstudianteListView.as_view(),   name='lista'),
    path('nuevo/',        views.EstudianteCreateView.as_view(), name='crear'),
    path('<int:pk>/',     views.EstudianteDetailView.as_view(), name='detalle'),
    path('<int:pk>/editar/',   views.EstudianteUpdateView.as_view(), name='editar'),
    path('<int:pk>/eliminar/', views.EstudianteDeleteView.as_view(), name='eliminar'),
]

urlpatterns = web_urlpatterns

# ── API REST (solo si DRF está instalado) ─────────────────────────────────────
try:
    from rest_framework.routers import DefaultRouter
    from .views import EstudianteViewSet

    router = DefaultRouter()
    router.register(r'estudiantes', EstudianteViewSet, basename='estudiante-api')

    # Agrega en tu urls.py principal:
    # path('api/', include('apps.estudiantes.urls_api')),
except ImportError:
    pass