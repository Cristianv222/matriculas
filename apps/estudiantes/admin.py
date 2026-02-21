from django.contrib import admin
from .models import Estudiante


@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ['nombre_completo', 'cedula', 'genero', 'representante', 'is_active']
    list_filter = ['genero', 'tiene_discapacidad', 'is_active']
    search_fields = ['nombres', 'apellidos', 'cedula']
    raw_id_fields = ['representante']
