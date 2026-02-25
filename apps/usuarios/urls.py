"""
============================================================
  MÓDULO: usuarios — urls.py
============================================================
"""
from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # ── Autenticación ─────────────────────────────────────────────────────────
    path('login/',                          views.LoginView.as_view(),          name='login'),
    path('logout/',                         views.LogoutView.as_view(),         name='logout'),
    path('registro/',                       views.RegistroView.as_view(),       name='registro'),
    path('verificar/<str:token>/',          views.VerificarEmailView.as_view(), name='verificar-email'),

    # ── Perfil y contraseña ───────────────────────────────────────────────────
    path('perfil/',                         views.PerfilView.as_view(),         name='perfil'),
    path('perfil/cambiar-password/',        views.CambioPasswordView.as_view(), name='cambio-password'),

    # ── Dashboards ────────────────────────────────────────────────────────────
    path('dashboard/',                      views.DashboardAdminView.as_view(),         name='dashboard-admin'),
    path('dashboard/representante/',        views.DashboardRepresentanteView.as_view(), name='dashboard-representante'),

    # ── Gestión (Admin/Secretaria) ────────────────────────────────────────────
    path('usuarios/',                       views.UsuarioListView.as_view(),   name='lista'),
    path('usuarios/crear/',                 views.UsuarioCreateView.as_view(), name='crear'),
    path('usuarios/<int:pk>/',              views.UsuarioDetailView.as_view(), name='detalle'),
    path('usuarios/<int:pk>/editar/',       views.UsuarioUpdateView.as_view(), name='editar'),
]