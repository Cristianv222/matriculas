"""
URLs del módulo de matrículas.

Prefijo sugerido en el router principal:
    path('matriculas/', include('apps.matriculas.urls', namespace='matriculas')),
"""
from django.urls import path
from . import views

app_name = 'matriculas'

urlpatterns = [
    # ── Representante / solicitante ────────────────────────────────────────
    path('',                    views.MatriculaListView.as_view(),      name='lista'),
    path('nueva/',              views.MatriculaCreateView.as_view(),    name='crear'),
    path('<int:pk>/',           views.MatriculaDetailView.as_view(),    name='detalle'),
    path('<int:pk>/editar/',    views.MatriculaUpdateView.as_view(),    name='editar'),
    path('<int:pk>/reenviar/',  views.MatriculaReenviarView.as_view(),  name='reenviar'),

    # ── Secretaría / personal ─────────────────────────────────────────────
    path('panel/',                          views.PanelSecretariaView.as_view(),      name='panel_secretaria'),
    path('<int:pk>/iniciar-revision/',      views.IniciarRevisionView.as_view(),      name='iniciar_revision'),
    path('<int:pk>/aprobar/',               views.AprobarMatriculaView.as_view(),     name='aprobar'),
    path('<int:pk>/rechazar/',              views.RechazarMatriculaView.as_view(),    name='rechazar'),

    # ── Administración ────────────────────────────────────────────────────
    path('<int:pk>/anular/',                views.AnularMatriculaView.as_view(),      name='anular'),

    # ── Historial ─────────────────────────────────────────────────────────
    path('<int:pk>/historial/',             views.HistorialMatriculaView.as_view(),   name='historial'),

    # ── API JSON (para AJAX / dashboards) ─────────────────────────────────
    path('api/estado/<int:pk>/',            views.MatriculaEstadoAPIView.as_view(),   name='api_estado'),
]