"""
============================================================
  MÓDULO: periodos — urls.py
============================================================
"""
from django.urls import path
from . import views

app_name = 'periodos'

urlpatterns = [
    # ── Períodos ──────────────────────────────────────────────────────────────
    path('periodos/',               views.PeriodoListView.as_view(),   name='periodo-lista'),
    path('periodos/nuevo/',         views.PeriodoCreateView.as_view(), name='periodo-crear'),
    path('periodos/<int:pk>/',      views.PeriodoDetailView.as_view(), name='periodo-detalle'),
    path('periodos/<int:pk>/editar/', views.PeriodoUpdateView.as_view(), name='periodo-editar'),

    # ── Niveles ───────────────────────────────────────────────────────────────
    path('niveles/',                views.NivelListView.as_view(),   name='nivel-lista'),
    path('niveles/nuevo/',          views.NivelCreateView.as_view(), name='nivel-crear'),
    path('niveles/<int:pk>/editar/', views.NivelUpdateView.as_view(), name='nivel-editar'),

    # ── Paralelos ─────────────────────────────────────────────────────────────
    path('paralelos/',              views.ParaleloListView.as_view(),   name='paralelo-lista'),
    path('paralelos/nuevo/',        views.ParaleloCreateView.as_view(), name='paralelo-crear'),
    path('paralelos/<int:pk>/editar/',   views.ParaleloUpdateView.as_view(),   name='paralelo-editar'),
    path('paralelos/<int:pk>/eliminar/', views.ParaleloDeleteView.as_view(),   name='paralelo-eliminar'),
]