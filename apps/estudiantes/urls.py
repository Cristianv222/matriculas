from django.urls import path
from . import views

app_name = 'estudiantes'

urlpatterns = [
    path('', views.lista_estudiantes, name='lista'),
    path('<int:pk>/', views.detalle_estudiante, name='detalle'),
]
