"""
============================================================
  MÓDULO: notificaciones
  Notificaciones internas del sistema + plantillas de email
============================================================
"""
from django.db import models
from apps.core.models import TimeStampedModel
from apps.usuarios.models import Usuario


class Notificacion(TimeStampedModel):
    """
    Notificación interna visible en el panel del usuario.
    Se complementa con envío de email mediante el servicio de notificaciones.
    """
    TIPO_INFO       = 'INFO'
    TIPO_EXITO      = 'EXITO'
    TIPO_ADVERTENCIA= 'ADVERTENCIA'
    TIPO_ERROR      = 'ERROR'

    TIPOS = [
        (TIPO_INFO,        'Información'),
        (TIPO_EXITO,       'Éxito'),
        (TIPO_ADVERTENCIA, 'Advertencia'),
        (TIPO_ERROR,       'Error'),
    ]

    # CSS de Bootstrap para renderizar el badge en el template
    TIPO_BADGE = {
        TIPO_INFO:        'info',
        TIPO_EXITO:       'success',
        TIPO_ADVERTENCIA: 'warning',
        TIPO_ERROR:       'danger',
    }

    # Bootstrap Icons para cada tipo
    TIPO_ICONO = {
        TIPO_INFO:        'bi-info-circle',
        TIPO_EXITO:       'bi-check-circle',
        TIPO_ADVERTENCIA: 'bi-exclamation-triangle',
        TIPO_ERROR:       'bi-x-circle',
    }

    # ─── Relaciones ───────────────────────────────────────────────────────────
    destinatario    = models.ForeignKey(Usuario, on_delete=models.CASCADE,
                                        related_name='notificaciones',
                                        verbose_name='Destinatario')
    generada_por    = models.ForeignKey(Usuario, on_delete=models.SET_NULL,
                                        null=True, blank=True,
                                        related_name='notificaciones_generadas',
                                        verbose_name='Generada por (usuario del sistema)')

    # ─── Contenido ────────────────────────────────────────────────────────────
    tipo            = models.CharField(max_length=15, choices=TIPOS,
                                       default=TIPO_INFO, verbose_name='Tipo')
    titulo          = models.CharField(max_length=200, verbose_name='Título')
    mensaje         = models.TextField(verbose_name='Mensaje')
    url_accion      = models.CharField(max_length=300, blank=True,
                                       verbose_name='URL de acción',
                                       help_text='Enlace al detalle de la matrícula o documento')
    texto_boton     = models.CharField(max_length=50, blank=True, default='Ver detalle',
                                       verbose_name='Texto del botón de acción')

    # ─── Estado de lectura ────────────────────────────────────────────────────
    leida           = models.BooleanField(default=False, verbose_name='Leída')
    fecha_lectura   = models.DateTimeField(blank=True, null=True, verbose_name='Fecha de lectura')

    # ─── Email ────────────────────────────────────────────────────────────────
    email_enviado   = models.BooleanField(default=False, verbose_name='Email enviado')
    fecha_email     = models.DateTimeField(blank=True, null=True,
                                           verbose_name='Fecha de envío del email')

    # ─── Referencia al objeto origen (matrícula, documento, etc.) ─────────────
    matricula       = models.ForeignKey(
                          'matriculas.Matricula', on_delete=models.SET_NULL,
                          null=True, blank=True,
                          related_name='notificaciones',
                          verbose_name='Matrícula relacionada'
                      )

    class Meta:
        verbose_name        = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering            = ['-created_at']
        indexes             = [
            models.Index(fields=['destinatario', 'leida']),
        ]

    def __str__(self):
        return f'[{self.get_tipo_display()}] {self.titulo} → {self.destinatario.username}'

    @property
    def badge_color(self):
        return self.TIPO_BADGE.get(self.tipo, 'secondary')

    @property
    def icono(self):
        return self.TIPO_ICONO.get(self.tipo, 'bi-bell')

    def marcar_como_leida(self):
        if not self.leida:
            from django.utils import timezone
            self.leida = True
            self.fecha_lectura = timezone.now()
            self.save(update_fields=['leida', 'fecha_lectura'])


class PlantillaEmail(TimeStampedModel):
    """
    Plantillas de email configurables desde el panel de administración.
    Usa variables del tipo {{ nombre_estudiante }}, {{ codigo_matricula }}, etc.
    """
    EVENTO_SOLICITUD_RECIBIDA = 'SOLICITUD_RECIBIDA'
    EVENTO_EN_REVISION        = 'EN_REVISION'
    EVENTO_APROBADA           = 'APROBADA'
    EVENTO_RECHAZADA          = 'RECHAZADA'
    EVENTO_DOC_RECHAZADO      = 'DOC_RECHAZADO'
    EVENTO_ANULADA            = 'ANULADA'

    EVENTOS = [
        (EVENTO_SOLICITUD_RECIBIDA, 'Solicitud de matrícula recibida'),
        (EVENTO_EN_REVISION,        'Matrícula en revisión'),
        (EVENTO_APROBADA,           'Matrícula aprobada'),
        (EVENTO_RECHAZADA,          'Matrícula rechazada'),
        (EVENTO_DOC_RECHAZADO,      'Documento rechazado'),
        (EVENTO_ANULADA,            'Matrícula anulada'),
    ]

    evento          = models.CharField(max_length=30, choices=EVENTOS,
                                       unique=True, verbose_name='Evento')
    asunto          = models.CharField(max_length=200, verbose_name='Asunto del email')
    cuerpo_html     = models.TextField(verbose_name='Cuerpo en HTML',
                                       help_text=(
                                           'Variables disponibles: {{ nombre_representante }}, '
                                           '{{ nombre_estudiante }}, {{ codigo_matricula }}, '
                                           '{{ estado_matricula }}, {{ motivo }}, '
                                           '{{ nombre_institucion }}'
                                       ))
    cuerpo_texto    = models.TextField(blank=True, verbose_name='Cuerpo en texto plano',
                                       help_text='Versión sin HTML para clientes de email básicos')

    class Meta:
        verbose_name        = 'Plantilla de Email'
        verbose_name_plural = 'Plantillas de Email'

    def __str__(self):
        return f'Email: {self.get_evento_display()}'


"""
============================================================
  MÓDULO: reportes
  No tiene modelos propios — usa los de los demás módulos.
  Esta sección documenta los queries más importantes.
============================================================

Los reportes se construyen a partir de queries sobre:

  1. Matricula.objects.filter(paralelo__periodo=periodo_activo)
     → Total de solicitudes, por estado, por tipo

  2. Paralelo.objects.annotate(
         total_matriculados=Count('matriculas', filter=Q(matriculas__estado='APROBADA'))
     )
     → Ocupación de cupos por paralelo y nivel

  3. Estudiante.objects.filter(
         matriculas__paralelo__periodo=periodo_activo,
         matriculas__estado='APROBADA'
     )
     → Nómina de estudiantes matriculados

  4. DocumentoMatricula.objects.filter(estado='PENDIENTE')
     → Documentos pendientes de verificación

  5. HistorialMatricula.objects.filter(...)
     → Auditoría y tiempos promedio de procesamiento

Los reportes se exportan a:
  - PDF con ReportLab / WeasyPrint
  - Excel con openpyxl
  - Tabla HTML imprimible

No se requieren modelos adicionales para el módulo de reportes.
============================================================
"""