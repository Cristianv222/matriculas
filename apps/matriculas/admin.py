from django.contrib import admin
from .models import Matricula, HistorialMatricula


class HistorialInline(admin.TabularInline):
    model = HistorialMatricula
    extra = 0
    readonly_fields = ['estado_anterior', 'estado_nuevo', 'usuario', 'fecha']


@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'estudiante', 'paralelo', 'tipo', 'estado', 'fecha_solicitud']
    list_filter = ['estado', 'tipo', 'paralelo__periodo']
    search_fields = ['codigo', 'estudiante__nombres', 'estudiante__apellidos', 'estudiante__cedula']
    inlines = [HistorialInline]
    readonly_fields = ['codigo', 'fecha_solicitud']
