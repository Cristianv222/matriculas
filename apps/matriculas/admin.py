from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.contrib import messages

from .models import Matricula, HistorialMatricula


# ─────────────────────────────────────────────────────────────────────────────
#  Inline: Historial dentro del detalle de Matrícula
# ─────────────────────────────────────────────────────────────────────────────
class HistorialMatriculaInline(admin.TabularInline):
    model = HistorialMatricula
    extra = 0
    readonly_fields = ('estado_anterior', 'estado_nuevo', 'usuario', 'fecha', 'comentario')
    can_delete = False
    ordering = ('fecha',)
    verbose_name = 'Evento de historial'
    verbose_name_plural = 'Historial de cambios de estado'

    def has_add_permission(self, request, obj=None):
        return False


# ─────────────────────────────────────────────────────────────────────────────
#  Admin: Matrícula
# ─────────────────────────────────────────────────────────────────────────────
@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    # ── Listado ───────────────────────────────────────────────────────────────
    list_display = (
        'codigo', 'estudiante', 'paralelo', 'tipo',
        'badge_estado', 'solicitante', 'fecha_solicitud', 'dias_en_proceso',
    )
    list_filter  = ('estado', 'tipo', 'paralelo__periodo', 'fecha_solicitud')
    search_fields = (
        'codigo',
        'estudiante__nombres', 'estudiante__apellidos',
        'estudiante__numero_identificacion',
        'solicitante__username', 'solicitante__email',
    )
    date_hierarchy  = 'fecha_solicitud'
    ordering        = ('-fecha_solicitud',)
    list_per_page   = 25

    # ── Formulario de detalle ─────────────────────────────────────────────────
    readonly_fields = (
        'codigo', 'fecha_solicitud', 'fecha_revision',
        'fecha_resolucion', 'fecha_anulacion',
        'numero_intentos', 'dias_en_proceso',
        'revisado_por', 'anulado_por',
        'badge_estado',
    )

    fieldsets = (
        ('Identificación', {
            'fields': ('codigo', 'badge_estado', 'tipo'),
        }),
        ('Participantes', {
            'fields': ('estudiante', 'paralelo', 'solicitante', 'matricula_anterior'),
        }),
        ('Estado y fechas', {
            'fields': (
                'estado',
                'fecha_solicitud', 'fecha_revision',
                'fecha_resolucion', 'fecha_anulacion',
                'numero_intentos', 'dias_en_proceso',
            ),
        }),
        ('Personal asignado', {
            'fields': ('revisado_por', 'anulado_por'),
        }),
        ('Notas y seguimiento', {
            'fields': ('observaciones', 'motivo_rechazo', 'motivo_anulacion'),
            'classes': ('collapse',),
        }),
    )

    inlines = [HistorialMatriculaInline]

    # ── Acciones personalizadas ───────────────────────────────────────────────
    actions = [
        'accion_iniciar_revision',
        'accion_aprobar',
        'accion_rechazar_generico',
        'accion_anular',
    ]

    @admin.action(description='✅ Iniciar revisión de matrículas seleccionadas')
    def accion_iniciar_revision(self, request, queryset):
        procesadas, errores = 0, 0
        for matricula in queryset:
            try:
                matricula.iniciar_revision(request.user)
                procesadas += 1
            except Exception as e:
                self.message_user(request, f'{matricula.codigo}: {e}', messages.ERROR)
                errores += 1
        if procesadas:
            self.message_user(request,
                f'{procesadas} matrícula(s) puesta(s) en revisión.', messages.SUCCESS)

    @admin.action(description='✔️ Aprobar matrículas seleccionadas')
    def accion_aprobar(self, request, queryset):
        procesadas, errores = 0, 0
        for matricula in queryset:
            try:
                matricula.aprobar(request.user)
                procesadas += 1
            except Exception as e:
                self.message_user(request, f'{matricula.codigo}: {e}', messages.ERROR)
                errores += 1
        if procesadas:
            self.message_user(request,
                f'{procesadas} matrícula(s) aprobada(s).', messages.SUCCESS)

    @admin.action(description='❌ Rechazar matrículas (motivo genérico de admin)')
    def accion_rechazar_generico(self, request, queryset):
        motivo = 'Rechazada por el administrador. Revise los documentos requeridos.'
        procesadas = 0
        for matricula in queryset:
            try:
                matricula.rechazar(request.user, motivo)
                procesadas += 1
            except Exception as e:
                self.message_user(request, f'{matricula.codigo}: {e}', messages.ERROR)
        if procesadas:
            self.message_user(request, f'{procesadas} matrícula(s) rechazada(s).', messages.WARNING)

    @admin.action(description='🚫 Anular matrículas aprobadas')
    def accion_anular(self, request, queryset):
        motivo = 'Anulada manualmente desde el panel de administración.'
        procesadas = 0
        for matricula in queryset:
            try:
                matricula.anular(request.user, motivo)
                procesadas += 1
            except Exception as e:
                self.message_user(request, f'{matricula.codigo}: {e}', messages.ERROR)
        if procesadas:
            self.message_user(request, f'{procesadas} matrícula(s) anulada(s).', messages.WARNING)

    # ── Columna con badge de color ────────────────────────────────────────────
    @admin.display(description='Estado', ordering='estado')
    def badge_estado(self, obj):
        colores = {
            Matricula.ESTADO_PENDIENTE:   ('#f59e0b', '⏳'),
            Matricula.ESTADO_EN_REVISION: ('#3b82f6', '🔍'),
            Matricula.ESTADO_APROBADA:    ('#10b981', '✅'),
            Matricula.ESTADO_RECHAZADA:   ('#ef4444', '❌'),
            Matricula.ESTADO_ANULADA:     ('#6b7280', '🚫'),
        }
        color, icono = colores.get(obj.estado, ('#9ca3af', '❓'))
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;'
            'border-radius:12px;font-size:0.8em;font-weight:600;">'
            '{} {}</span>',
            color, icono, obj.get_estado_display(),
        )

    # ── Protecciones de edición ───────────────────────────────────────────────
    def get_readonly_fields(self, request, obj=None):
        """Hace inmutables los campos clave en matrículas finalizadas."""
        base = list(self.readonly_fields)
        if obj and obj.esta_finalizada:
            base += ['estudiante', 'paralelo', 'solicitante', 'tipo', 'estado']
        return base

    def has_delete_permission(self, request, obj=None):
        """Solo superusuarios pueden eliminar registros de matrícula."""
        return request.user.is_superuser


# ─────────────────────────────────────────────────────────────────────────────
#  Admin: Historial (solo lectura)
# ─────────────────────────────────────────────────────────────────────────────
@admin.register(HistorialMatricula)
class HistorialMatriculaAdmin(admin.ModelAdmin):
    list_display  = ('matricula', 'estado_anterior', 'flecha_estado', 'estado_nuevo',
                     'usuario', 'fecha', 'comentario_corto')
    list_filter   = ('estado_nuevo', 'fecha')
    search_fields = ('matricula__codigo', 'usuario__username', 'comentario')
    readonly_fields = ('matricula', 'estado_anterior', 'estado_nuevo',
                       'usuario', 'fecha', 'comentario')
    ordering = ('-fecha',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    @admin.display(description='→')
    def flecha_estado(self, obj):
        return format_html('<strong style="color:#6366f1;">→</strong>')

    @admin.display(description='Comentario')
    def comentario_corto(self, obj):
        return (obj.comentario[:60] + '…') if len(obj.comentario) > 60 else obj.comentario