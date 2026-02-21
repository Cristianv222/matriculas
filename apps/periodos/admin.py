from django.contrib import admin
from .models import PeriodoAcademico, Nivel, Paralelo


@admin.register(PeriodoAcademico)
class PeriodoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'fecha_inicio', 'fecha_fin', 'es_activo']
    list_filter = ['es_activo']


@admin.register(Nivel)
class NivelAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'orden']
    ordering = ['orden']


@admin.register(Paralelo)
class ParaleloAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'cupo_maximo', 'cupo_disponible', 'is_active']
    list_filter = ['periodo', 'nivel']
