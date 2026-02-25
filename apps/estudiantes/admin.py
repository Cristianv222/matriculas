"""
============================================================
  MÓDULO: estudiantes — admin.py
============================================================
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Estudiante


@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):

    # ─── Listado ──────────────────────────────────────────────────────────────
    list_display = [
        'foto_thumbnail', 'nombre_completo', 'cedula', 'edad',
        'genero', 'ciudad', 'representante',
        'badge_atencion_especial', 'created_at',
    ]
    list_display_links = ['foto_thumbnail', 'nombre_completo']
    list_filter = [
        'genero', 'etnia', 'ciudad',
        'tiene_discapacidad', 'tipo_sangre',
        ('created_at', admin.DateFieldListFilter),
    ]
    search_fields = [
        'nombres', 'apellidos', 'cedula',
        'padre_nombres', 'madre_nombres',
        'representante__first_name', 'representante__last_name',
        'representante__email',
    ]
    ordering = ['apellidos', 'nombres']
    list_per_page = 25
    date_hierarchy = 'created_at'

    # ─── Campos de solo lectura ───────────────────────────────────────────────
    readonly_fields = [
        'foto_preview', 'nombre_completo', 'edad',
        'requiere_atencion_especial', 'tiene_datos_medicos',
        'created_at', 'updated_at',
    ]

    # ─── Fieldsets ────────────────────────────────────────────────────────────
    fieldsets = (
        ('👤 Datos de Identidad', {
            'fields': (
                ('nombres', 'apellidos'),
                ('cedula', 'nacionalidad'),
                ('fecha_nacimiento', 'genero'),
                ('etnia', 'lugar_nacimiento'),
                ('foto', 'foto_preview'),
            ),
        }),
        ('📍 Dirección y Contacto de Emergencia', {
            'fields': (
                'direccion',
                ('ciudad', 'sector'),
                ('contacto_emergencia', 'telefono_emergencia'),
            ),
            'classes': ('collapse',),
        }),
        ('🩺 Datos Médicos', {
            'fields': (
                'tipo_sangre',
                'alergias',
                'enfermedades_cronicas',
                'medicacion_actual',
                ('medico_tratante', 'seguro_medico'),
                'tiene_datos_medicos',
            ),
            'classes': ('collapse',),
        }),
        ('♿ Discapacidad', {
            'fields': (
                'tiene_discapacidad',
                ('tipo_discapacidad', 'porcentaje_discapacidad'),
                'numero_conadis',
                'necesidades_especiales',
            ),
            'classes': ('collapse',),
        }),
        ('👨‍👩‍👦 Representante Legal', {
            'fields': (
                ('representante', 'relacion_representante'),
            ),
        }),
        ('👨 Datos del Padre', {
            'fields': (
                'padre_nombres',
                ('padre_cedula', 'padre_telefono'),
                ('padre_email', 'padre_ocupacion'),
                ('padre_estado_civil', 'padre_instruccion'),
            ),
            'classes': ('collapse',),
        }),
        ('👩 Datos de la Madre', {
            'fields': (
                'madre_nombres',
                ('madre_cedula', 'madre_telefono'),
                ('madre_email', 'madre_ocupacion'),
                ('madre_estado_civil', 'madre_instruccion'),
            ),
            'classes': ('collapse',),
        }),
        ('🏫 Procedencia Académica', {
            'fields': (
                'institucion_anterior',
                ('amie_anterior', 'grado_anterior'),
                ('anio_anterior', 'promedio_anterior'),
                'motivo_cambio',
            ),
            'classes': ('collapse',),
        }),
        ('📝 Observaciones', {
            'fields': ('observaciones_generales',),
            'classes': ('collapse',),
        }),
        ('⚙️ Información del Sistema', {
            'fields': (
                'nombre_completo', 'edad',
                'requiere_atencion_especial',
                ('created_at', 'updated_at'),
            ),
            'classes': ('collapse',),
        }),
    )

    # ─── Métodos de display ───────────────────────────────────────────────────
    @admin.display(description='Foto')
    def foto_thumbnail(self, obj):
        if obj.foto:
            return format_html(
                '<img src="{}" style="width:40px;height:40px;'
                'border-radius:50%;object-fit:cover;" />',
                obj.foto.url
            )
        initials = f"{obj.apellidos[0]}{obj.nombres[0]}".upper() if obj.apellidos and obj.nombres else '?'
        return format_html(
            '<div style="width:40px;height:40px;border-radius:50%;'
            'background:#6c757d;color:white;display:flex;'
            'align-items:center;justify-content:center;'
            'font-size:14px;font-weight:bold;">{}</div>',
            initials
        )

    @admin.display(description='Vista previa')
    def foto_preview(self, obj):
        if obj.foto:
            return format_html(
                '<img src="{}" style="max-height:200px;border-radius:8px;" />',
                obj.foto.url
            )
        return '— Sin foto —'

    @admin.display(description='⚠️ Atención especial', boolean=True)
    def badge_atencion_especial(self, obj):
        return obj.requiere_atencion_especial

    # ─── Acciones ──────────────────────────────────────────────────────────────
    actions = ['exportar_fichas_basicas']

    @admin.action(description='Exportar datos básicos de estudiantes seleccionados')
    def exportar_fichas_basicas(self, request, queryset):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="estudiantes.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Apellidos', 'Nombres', 'Cédula', 'Fecha Nacimiento',
            'Género', 'Ciudad', 'Representante', 'Teléfono Emergencia'
        ])
        for e in queryset:
            writer.writerow([
                e.apellidos, e.nombres, e.cedula or '',
                e.fecha_nacimiento.strftime('%d/%m/%Y') if e.fecha_nacimiento else '',
                e.get_genero_display(), e.ciudad,
                str(e.representante) if e.representante else '',
                e.telefono_emergencia,
            ])
        return response