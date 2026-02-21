from django.urls import path
from . import views

app_name = 'documentos'

urlpatterns = [
    path('matricula/<int:matricula_pk>/', views.lista_documentos_matricula, name='lista'),
]
