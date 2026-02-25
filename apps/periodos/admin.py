"""
============================================================
  MÓDULO: periodos — admin.py
============================================================
"""
from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import PeriodoAcademico, Nivel, Paralelo


# ══════════════════════════════════════════════════════════════════════════════
#  PERÍODO ACADÉMICO
# ══════════════════════════════════════════════════════════════════════════════

@admin.register(PeriodoAcademico)
class PeriodoAcademicoAdmin(admin.ModelAdmin):

    list_display = [
        'nombre', 'regimen', 'fecha_inicio', 'fecha_fin',
        'badge_estado_matriculas', 'badge_activo',
        'total_paralelos', 'total_matriculas',
    ]
    list_filter  = ['regimen', 'es_activo', 'permite_matricula_extra']
    search_fields = ['nombre', 'observaciones']
    ordering      = ['-fecha_inicio']
    readonly_fields = [
        'badge_estado_matriculas', 'badge_activo',
        'total_paralelos', 'total_matriculas',
        'created_at', 'updated_at',
    ]

    fieldsets = (
        ('📅 Datos Generales', {
            'fields': (
                ('nombre', 'regimen'),
                ('fecha_inicio', 'fecha_fin'),
                ('es_activo',),
            ),
        }),
        ('📋 Ventana de Matrículas', {
            'fields': (
                ('fecha_inicio_matriculas', 'fecha_fin_matriculas'),
            ),
        }),
        ('⭐ Matrículas Extraordinarias', {
            'fields': (
                'permite_matricula_extra',
                ('fecha_inicio_extra', 'fecha_fin_extra'),
            ),
            'classes': ('collapse',),
        }),
        ('📝 Observaciones', {
            'fields': ('observaciones',),
            'classes': ('collapse',),
        }),
        ('📊 Estadísticas (solo lectura)', {
            'fields': (
                'badge_estado_matriculas',
                ('total_paralelos', 'total_matriculas'),
            ),
            'classes': ('collapse',),
        }),
        ('⚙️ Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    # ── Display methods ───────────────────────────────────────────────────────
    @admin.display(description='Estado matrícula')
    def badge_estado_matriculas(self, obj):
        hoy = timezone.now().date()
        if obj.matriculas_abiertas:
            return format_html('<span style="color:green;font-weight:bold;">✅ Regulares abiertas</span>')
        if obj.matriculas_extraordinarias_abiertas:
            return format_html('<span style="color:orange;font-weight:bold;">⭐ Extraordinarias abiertas</span>')
        if obj.fecha_fin_matriculas and hoy > obj.fecha_fin_matriculas:
            return format_html('<span style="color:red;">🔒 Cerradas</span>')
        if obj.fecha_inicio_matriculas and hoy < obj.fecha_inicio_matriculas:
            return format_html('<span style="color:gray;">⏳ Aún no inician</span>')
        return '—'

    @admin.display(description='Activo', boolean=True)
    def badge_activo(self, obj):
        return obj.es_activo

    @admin.display(description='Paralelos')
    def total_paralelos(self, obj):
        return obj.paralelos.count()

    @admin.display(description='Matrículas')
    def total_matriculas(self, obj):
        from apps.matriculas.models import Matricula
        total    = Matricula.objects.filter(paralelo__periodo=obj).count()
        aprobadas = Matricula.objects.filter(
            paralelo__periodo=obj, estado=Matricula.ESTADO_APROBADA
        ).count()
        return format_html('{} total / <strong>{} aprobadas</strong>', total, aprobadas)

    # ── Acciones ──────────────────────────────────────────────────────────────
    actions = ['activar_periodo', 'abrir_matriculas_extraordinarias']

    @admin.action(description='Activar período seleccionado (desactiva los demás)')
    def activar_periodo(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, 'Seleccione exactamente un período para activar.', level='error')
            return
        periodo = queryset.first()
        PeriodoAcademico.objects.exclude(pk=periodo.pk).update(es_activo=False)
        periodo.es_activo = True
        periodo.save()
        self.message_user(request, f'Período "{periodo}" activado.')

    @admin.action(description='Habilitar matrículas extraordinarias')
    def abrir_matriculas_extraordinarias(self, request, queryset):
        queryset.update(permite_matricula_extra=True)
        self.message_user(request, f'{queryset.count()} período(s) actualizados.')


# ══════════════════════════════════════════════════════════════════════════════
#  NIVEL
# ══════════════════════════════════════════════════════════════════════════════

@admin.register(Nivel)
class NivelAdmin(admin.ModelAdmin):

    list_display  = ['nombre', 'subnivel', 'orden', 'descripcion', 'total_paralelos']
    list_filter   = ['subnivel']
    search_fields = ['nombre', 'descripcion']
    ordering      = ['orden']
    list_editable = ['orden']  # Edición rápida de orden en listado

    fieldsets = (
        ('📚 Datos del Nivel', {
            'fields': (
                ('nombre', 'subnivel'),
                ('orden', 'descripcion'),
            ),
        }),
        ('⚙️ Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ['created_at', 'updated_at']

    @admin.display(description='Paralelos')
    def total_paralelos(self, obj):
        return obj.paralelos.count()


# ══════════════════════════════════════════════════════════════════════════════
#  PARALELO — con inline de matrículas
# ══════════════════════════════════════════════════════════════════════════════

class ParaleloInline(admin.TabularInline):
    """Permite ver/crear paralelos directamente desde el Período."""
    model           = Paralelo
    extra           = 0
    fields          = ['nivel', 'nombre', 'jornada', 'cupo_maximo',
                       'badge_cupo', 'badge_ocupacion']
    readonly_fields = ['badge_cupo', 'badge_ocupacion']
    show_change_link = True

    @admin.display(description='Cupo disp.')
    def badge_cupo(self, obj):
        if not obj.pk:
            return '—'
        disp = obj.cupo_disponible
        color = 'green' if disp > 5 else ('orange' if disp > 0 else 'red')
        return format_html('<strong style="color:{};">{}</strong>', color, disp)

    @admin.display(description='Ocupación')
    def badge_ocupacion(self, obj):
        if not obj.pk:
            return '—'
        pct   = obj.porcentaje_ocupacion
        color = 'green' if pct < 70 else ('orange' if pct < 95 else 'red')
        return format_html('<span style="color:{};">{}%</span>', color, pct)


# Añadir el inline al PeriodoAcademicoAdmin
PeriodoAcademicoAdmin.inlines = [ParaleloInline]


@admin.register(Paralelo)
class ParaleloAdmin(admin.ModelAdmin):

    list_display = [
        'periodo', 'nivel', 'nombre', 'jornada',
        'cupo_maximo', 'badge_cupo_disponible', 'badge_ocupacion', 'badge_lleno',
    ]
    list_filter  = [
        'periodo', 'nivel__subnivel', 'jornada',
        ('periodo__es_activo', admin.BooleanFieldListFilter),
    ]
    search_fields = ['nivel__nombre', 'nombre', 'periodo__nombre']
    ordering      = ['periodo', 'nivel__orden', 'nombre']
    readonly_fields = [
        'matriculados_aprobados', 'cupo_disponible',
        'cupo_lleno', 'porcentaje_ocupacion',
        'created_at', 'updated_at',
    ]

    fieldsets = (
        ('📋 Configuración del Paralelo', {
            'fields': (
                ('periodo', 'nivel'),
                ('nombre', 'jornada'),
                'cupo_maximo',
                'observaciones',
            ),
        }),
        ('📊 Cupo en tiempo real (solo lectura)', {
            'fields': (
                ('matriculados_aprobados', 'cupo_disponible'),
                ('cupo_lleno', 'porcentaje_ocupacion'),
            ),
        }),
        ('⚙️ Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Cupo disp.')
    def badge_cupo_disponible(self, obj):
        disp  = obj.cupo_disponible
        color = 'green' if disp > 5 else ('orange' if disp > 0 else 'red')
        return format_html('<strong style="color:{};">{} / {}</strong>',
                           color, disp, obj.cupo_maximo)

    @admin.display(description='Ocupación')
    def badge_ocupacion(self, obj):
        pct   = obj.porcentaje_ocupacion
        color = 'green' if pct < 70 else ('orange' if pct < 95 else 'red')
        return format_html(
            '<div style="background:#eee;border-radius:4px;width:80px;">'
            '<div style="background:{};border-radius:4px;width:{}%;'
            'text-align:center;color:white;font-size:11px;">{:.0f}%</div>'
            '</div>',
            color, min(pct, 100), pct
        )

    @admin.display(description='¿Lleno?', boolean=True)
    def badge_lleno(self, obj):
        return obj.cupo_lleno

    actions = ['duplicar_paralelos']

    @admin.action(description='Duplicar paralelos seleccionados al período activo')
    def duplicar_paralelos(self, request, queryset):
        periodo_activo = PeriodoAcademico.get_activo()
        if not periodo_activo:
            self.message_user(request, 'No hay un período activo configurado.', level='error')
            return
        creados = 0
        for p in queryset:
            _, created = Paralelo.objects.get_or_create(
                periodo=periodo_activo,
                nivel=p.nivel,
                nombre=p.nombre,
                defaults={
                    'cupo_maximo': p.cupo_maximo,
                    'jornada': p.jornada,
                }
            )
            if created:
                creados += 1
        self.message_user(
            request,
            f'{creados} paralelo(s) creados en "{periodo_activo}". '
            f'{queryset.count() - creados} ya existían.'
        )