from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'get_full_name', 'cedula', 'email', 'rol', 'is_active']
    list_filter = ['rol', 'is_active']
    search_fields = ['username', 'first_name', 'last_name', 'cedula', 'email']
    fieldsets = UserAdmin.fieldsets + (
        ('Datos adicionales', {'fields': ('rol', 'cedula', 'telefono', 'foto', 'fecha_nacimiento', 'direccion', 'is_verified')}),
    )
