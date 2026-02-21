from django.urls import path
from . import views

app_name = 'periodos'

urlpatterns = [
    path('paralelos/', views.lista_paralelos, name='paralelos'),
]
