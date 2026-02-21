from django.urls import path
from . import views

app_name = 'matriculas'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('lista/', views.lista_matriculas, name='lista'),
    path('<int:pk>/', views.detalle_matricula, name='detalle'),
]
