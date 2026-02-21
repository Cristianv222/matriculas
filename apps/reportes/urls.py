from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.dashboard_reportes, name='dashboard'),
    path('matriculados/', views.reporte_matriculados, name='matriculados'),
]
