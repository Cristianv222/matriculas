"""
============================================================
  URLs: apps.documentos
============================================================
"""
from django.urls import path
from . import views

app_name = 'documentos'

urlpatterns = [
    # ── Por matrícula ─────────────────────────────────────────────────────────
    path('matricula/<int:matricula_pk>/',
         views.DocumentosMatriculaView.as_view(), name='lista'),

    path('matricula/<int:matricula_pk>/subir/<int:tipo_pk>/',
         views.SubirDocumentoView.as_view(), name='subir'),

    # ── Por documento ─────────────────────────────────────────────────────────
    path('<int:pk>/descargar/',
         views.DescargarDocumentoView.as_view(), name='descargar'),

    path('<int:pk>/eliminar/',
         views.EliminarDocumentoView.as_view(), name='eliminar'),

    path('<int:pk>/verificar/',
         views.VerificarDocumentoView.as_view(), name='verificar'),

    path('<int:pk>/rechazar/',
         views.RechazarDocumentoView.as_view(), name='rechazar'),

    # ── Panel secretaría ──────────────────────────────────────────────────────
    path('panel/',
         views.PanelDocumentosView.as_view(), name='panel'),
]