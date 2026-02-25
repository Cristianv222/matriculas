"""
============================================================
  MÓDULO: usuarios — admin.py
============================================================
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils import timezone
from .models import Usuario, SesionUsuario


# ══════════════════════════════════════════════════════════════════════════════
#  INLINE: Sesiones recientes del usuario
# ══════════════════════════════════════════════════════════════════════════════

class SesionUsuarioInline(admin.TabularInline):
    model          = SesionUsuario
    extra          = 0
    max_num        = 10
    can_delete     = False
    readonly_fields = ['ip', 'user_agent_corto', 'fecha_login', 'fecha_logout', 'exitosa']
    fields          = ['ip', 'user_agent_corto', 'fecha_login', 'fecha_logout', 'exitosa']
    ordering        = ['-fecha_login']
    verbose_name_plural = 'Últimas 10 sesiones'

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description='Navegador')
    def user_agent_corto(self, obj):
        return obj.user_agent[:80] + '…' if len(obj.user_agent) > 80 else obj.user_agent


# ══════════════════════════════════════════════════════════════════════════════
#  USUARIO
# ══════════════════════════════════════════════════════════════════════════════

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """
    Extiende UserAdmin para incluir los campos personalizados.
    Conserva toda la funcionalidad nativa de Django (cambio de contraseña, permisos, etc.)
    """

    inlines = [SesionUsuarioInline]

    # ── Listado ───────────────────────────────────────────────────────────────
    list_display = [
        'foto_thumbnail', 'username', 'nombre_completo_display',
        'cedula', 'badge_rol', 'email',
        'telefono', 'badge_verificado', 'is_active', 'date_joined',
    ]
    list_display_links = ['foto_thumbnail', 'username']
    list_filter = [
        'rol', 'is_active', 'is_verified', 'is_staff',
        ('date_joined', admin.DateFieldListFilter),
    ]
    search_fields = [
        'username', 'first_name', 'last_name',
        'email', 'cedula', 'telefono',
    ]
    ordering      = ['last_name', 'first_name']
    list_per_page = 25

    # ── Fieldsets (reemplaza los de UserAdmin) ────────────────────────────────
    fieldsets = (
        ('🔐 Credenciales', {
            'fields': ('username', 'password'),
        }),
        ('👤 Datos Personales', {
            'fields': (
                ('first_name', 'last_name'),
                'email',
                ('cedula', 'fecha_nacimiento'),
                ('telefono', 'telefono_alt'),
                'direccion',
                ('ciudad', 'sector'),
                ('foto', 'foto_preview'),
            ),
        }),
        ('🎭 Rol y Permisos', {
            'fields': (
                'rol',
                ('is_active', 'is_verified'),
                ('is_staff', 'is_superuser'),
                'groups',
                'user_permissions',
            ),
        }),
        ('🔑 Verificación de Email', {
            'fields': (
                'token_verificacion',
                'token_expiracion',
                'ultimo_acceso_ip',
            ),
            'classes': ('collapse',),
        }),
        ('📅 Fechas del Sistema', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',),
        }),
    )

    # Fieldset para creación de nuevo usuario
    add_fieldsets = (
        ('🔐 Credenciales', {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        ('👤 Datos Básicos', {
            'fields': (
                ('first_name', 'last_name'),
                'email', 'cedula', 'rol',
                ('telefono', 'telefono_alt'),
            ),
        }),
    )

    readonly_fields = ['foto_preview', 'last_login', 'date_joined', 'ultimo_acceso_ip']

    # ── Display methods ───────────────────────────────────────────────────────
    @admin.display(description='Foto')
    def foto_thumbnail(self, obj):
        if obj.foto:
            return format_html(
                '<img src="{}" style="width:38px;height:38px;'
                'border-radius:50%;object-fit:cover;" />',
                obj.foto.url
            )
        initials = f"{obj.last_name[0]}{obj.first_name[0]}".upper() \
            if obj.last_name and obj.first_name else obj.username[0].upper()
        color = {
            'ADMIN':         '#dc3545',
            'SECRETARIA':    '#0d6efd',
            'REPRESENTANTE': '#198754',
            'DOCENTE':       '#6f42c1',
        }.get(obj.rol, '#6c757d')
        return format_html(
            '<div style="width:38px;height:38px;border-radius:50%;'
            'background:{};color:white;display:flex;align-items:center;'
            'justify-content:center;font-size:13px;font-weight:bold;">{}</div>',
            color, initials
        )

    @admin.display(description='Nombre')
    def nombre_completo_display(self, obj):
        return obj.nombre_completo

    @admin.display(description='Rol')
    def badge_rol(self, obj):
        colores = {
            'ADMIN':         ('#dc3545', '🛡️'),
            'SECRETARIA':    ('#0d6efd', '📋'),
            'REPRESENTANTE': ('#198754', '👨‍👩‍👦'),
            'DOCENTE':       ('#6f42c1', '📚'),
        }
        color, icono = colores.get(obj.rol, ('#6c757d', '👤'))
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;'
            'border-radius:10px;font-size:11px;">{} {}</span>',
            color, icono, obj.get_rol_display()
        )

    @admin.display(description='✉️ Verificado', boolean=True)
    def badge_verificado(self, obj):
        return obj.is_verified

    @admin.display(description='Vista previa')
    def foto_preview(self, obj):
        if obj.foto:
            return format_html(
                '<img src="{}" style="max-height:150px;border-radius:8px;" />',
                obj.foto.url
            )
        return '— Sin foto —'

    # ── Acciones ──────────────────────────────────────────────────────────────
    actions = [
        'verificar_emails', 'desactivar_usuarios',
        'activar_usuarios', 'cambiar_rol_representante',
    ]

    @admin.action(description='Marcar emails como verificados')
    def verificar_emails(self, request, queryset):
        updated = queryset.update(is_verified=True, token_verificacion='')
        self.message_user(request, f'{updated} usuario(s) verificados.')

    @admin.action(description='Desactivar usuarios seleccionados')
    def desactivar_usuarios(self, request, queryset):
        # Proteger superusuarios
        qs = queryset.exclude(is_superuser=True)
        updated = qs.update(is_active=False)
        self.message_user(request, f'{updated} usuario(s) desactivados.')

    @admin.action(description='Activar usuarios seleccionados')
    def activar_usuarios(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} usuario(s) activados.')

    @admin.action(description='Cambiar rol a Representante Legal')
    def cambiar_rol_representante(self, request, queryset):
        qs = queryset.exclude(is_superuser=True)
        updated = qs.update(rol=Usuario.ROL_REPRESENTANTE)
        self.message_user(request, f'{updated} usuario(s) actualizados a Representante.')


# ══════════════════════════════════════════════════════════════════════════════
#  SESIÓN DE USUARIO
# ══════════════════════════════════════════════════════════════════════════════

@admin.register(SesionUsuario)
class SesionUsuarioAdmin(admin.ModelAdmin):

    list_display  = ['usuario', 'ip', 'user_agent_corto', 'fecha_login', 'fecha_logout', 'exitosa']
    list_filter   = ['exitosa', ('fecha_login', admin.DateFieldListFilter)]
    search_fields = ['usuario__username', 'usuario__email', 'ip']
    ordering      = ['-fecha_login']
    list_per_page = 50
    readonly_fields = ['usuario', 'ip', 'user_agent', 'fecha_login', 'fecha_logout', 'exitosa']

    # Solo lectura: las sesiones son registros de auditoría, no se editan
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description='Navegador / Dispositivo')
    def user_agent_corto(self, obj):
        return obj.user_agent[:60] + '…' if len(obj.user_agent) > 60 else obj.user_agent

    actions = ['purgar_sesiones_antiguas']

    @admin.action(description='Purgar sesiones con más de 90 días')
    def purgar_sesiones_antiguas(self, request, queryset):
        desde = timezone.now() - timezone.timedelta(days=90)
        eliminadas, _ = SesionUsuario.objects.filter(fecha_login__lt=desde).delete()
        self.message_user(request, f'{eliminadas} sesiones antiguas eliminadas.')