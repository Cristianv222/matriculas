"""
============================================================
  MÓDULO: matriculas
  Proceso completo del flujo de matrícula y su historial
============================================================
"""
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from apps.core.models import TimeStampedModel
from apps.usuarios.models import Usuario
from apps.estudiantes.models import Estudiante
from apps.periodos.models import Paralelo


class Matricula(TimeStampedModel):
    """
    Solicitud y proceso completo de matrícula de un estudiante.

    Flujo de estados:
    PENDIENTE → EN_REVISION → APROBADA
                           → RECHAZADA → (el representante corrige y vuelve a PENDIENTE)
    APROBADA  → ANULADA   (caso excepcional, solo Admin)

    Tipos:
    - NUEVA        : Primera vez en la institución
    - RENOVACION   : Continuación al siguiente año en la misma institución
    - TRASLADO_ENTRADA : Viene de otra institución mid-año
    """
    # ── Estados ───────────────────────────────────────────────────────────────
    ESTADO_PENDIENTE   = 'PENDIENTE'
    ESTADO_EN_REVISION = 'EN_REVISION'
    ESTADO_APROBADA    = 'APROBADA'
    ESTADO_RECHAZADA   = 'RECHAZADA'
    ESTADO_ANULADA     = 'ANULADA'

    ESTADOS = [
        (ESTADO_PENDIENTE,   'Pendiente de revisión'),
        (ESTADO_EN_REVISION, 'En revisión'),
        (ESTADO_APROBADA,    'Aprobada'),
        (ESTADO_RECHAZADA,   'Rechazada - Requiere correcciones'),
        (ESTADO_ANULADA,     'Anulada'),
    ]

    ESTADOS_FINALES   = [ESTADO_APROBADA, ESTADO_ANULADA]
    ESTADOS_EDITABLES = [ESTADO_PENDIENTE, ESTADO_RECHAZADA]

    # ── Tipos de matrícula ────────────────────────────────────────────────────
    TIPO_NUEVA           = 'NUEVA'
    TIPO_RENOVACION      = 'RENOVACION'
    TIPO_TRASLADO_ENTRADA = 'TRASLADO_ENTRADA'

    TIPOS = [
        (TIPO_NUEVA,            'Primera matrícula'),
        (TIPO_RENOVACION,       'Renovación de matrícula'),
        (TIPO_TRASLADO_ENTRADA, 'Traslado desde otra institución'),
    ]

    # ─── Datos principales ───────────────────────────────────────────────────
    codigo           = models.CharField(max_length=20, unique=True,
                                        verbose_name='Código de matrícula',
                                        help_text='Generado automáticamente')
    estudiante       = models.ForeignKey(Estudiante, on_delete=models.CASCADE,
                                         related_name='matriculas',
                                         verbose_name='Estudiante')
    paralelo         = models.ForeignKey(Paralelo, on_delete=models.CASCADE,
                                         related_name='matriculas',
                                         verbose_name='Paralelo asignado')
    solicitante      = models.ForeignKey(Usuario, on_delete=models.CASCADE,
                                         related_name='matriculas_solicitadas',
                                         verbose_name='Representante solicitante')
    tipo             = models.CharField(max_length=20, choices=TIPOS,
                                        default=TIPO_NUEVA, verbose_name='Tipo de matrícula')
    estado           = models.CharField(max_length=15, choices=ESTADOS,
                                        default=ESTADO_PENDIENTE, verbose_name='Estado')

    # ─── Control de flujo y fechas ───────────────────────────────────────────
    fecha_solicitud  = models.DateTimeField(auto_now_add=True,
                                            verbose_name='Fecha de solicitud')
    fecha_revision   = models.DateTimeField(blank=True, null=True,
                                            verbose_name='Fecha de inicio de revisión')
    fecha_resolucion = models.DateTimeField(blank=True, null=True,
                                            verbose_name='Fecha de aprobación / rechazo')
    fecha_anulacion  = models.DateTimeField(blank=True, null=True,
                                            verbose_name='Fecha de anulación')

    # ─── Personal que interviene ─────────────────────────────────────────────
    revisado_por     = models.ForeignKey(Usuario, on_delete=models.SET_NULL,
                                         null=True, blank=True,
                                         related_name='matriculas_revisadas',
                                         verbose_name='Revisado por')
    anulado_por      = models.ForeignKey(Usuario, on_delete=models.SET_NULL,
                                         null=True, blank=True,
                                         related_name='matriculas_anuladas',
                                         verbose_name='Anulado por')

    # ─── Notas y seguimiento ─────────────────────────────────────────────────
    observaciones    = models.TextField(blank=True,
                                        verbose_name='Observaciones internas',
                                        help_text='Notas del personal (no visible al representante)')
    motivo_rechazo   = models.TextField(blank=True,
                                        verbose_name='Motivo de rechazo',
                                        help_text='Visible al representante. Explique qué debe corregir.')
    motivo_anulacion = models.TextField(blank=True,
                                        verbose_name='Motivo de anulación')

    # ─── Matrícula anterior (para renovaciones) ───────────────────────────────
    matricula_anterior = models.ForeignKey('self', on_delete=models.SET_NULL,
                                           null=True, blank=True,
                                           related_name='matricula_siguiente',
                                           verbose_name='Matrícula del período anterior')

    # ─── Número de intentos (para control de rechazos) ───────────────────────
    numero_intentos  = models.PositiveIntegerField(default=0,
                                                   verbose_name='Número de veces rechazada')

    class Meta:
        verbose_name        = 'Matrícula'
        verbose_name_plural = 'Matrículas'
        ordering            = ['-fecha_solicitud']
        indexes             = [
            models.Index(fields=['codigo']),
            models.Index(fields=['estado']),
            models.Index(fields=['estudiante', 'paralelo']),
        ]

    def __str__(self):
        return f'{self.codigo} — {self.estudiante}'

    def clean(self):
        # Validar que no exista matrícula aprobada para este estudiante
        # en el mismo período
        if self.paralelo_id and self.estudiante_id:
            duplicada = Matricula.objects.filter(
                estudiante=self.estudiante,
                paralelo__periodo=self.paralelo.periodo,
                estado=self.ESTADO_APROBADA,
            ).exclude(pk=self.pk)
            if duplicada.exists():
                raise ValidationError(
                    'Este estudiante ya tiene una matrícula aprobada en este período académico.'
                )

    def save(self, *args, **kwargs):
        if not self.codigo:
            from apps.core.utils import generar_codigo_matricula
            self.codigo = generar_codigo_matricula()
        super().save(*args, **kwargs)

    # ─── Métodos de transición de estado ─────────────────────────────────────
    def iniciar_revision(self, usuario):
        """Secretaría toma la solicitud para revisarla."""
        if self.estado != self.ESTADO_PENDIENTE:
            raise ValidationError('Solo se puede iniciar revisión desde estado PENDIENTE.')
        self.estado = self.ESTADO_EN_REVISION
        self.revisado_por = usuario
        self.fecha_revision = timezone.now()
        self.save()
        self._registrar_historial(self.ESTADO_PENDIENTE, self.ESTADO_EN_REVISION, usuario)

    def aprobar(self, usuario, observaciones=''):
        """Aprueba la matrícula."""
        if self.estado != self.ESTADO_EN_REVISION:
            raise ValidationError('Solo se puede aprobar desde estado EN_REVISION.')
        self.estado = self.ESTADO_APROBADA
        self.fecha_resolucion = timezone.now()
        self.revisado_por = usuario
        if observaciones:
            self.observaciones = observaciones
        self.save()
        self._registrar_historial(self.ESTADO_EN_REVISION, self.ESTADO_APROBADA, usuario, observaciones)

    def rechazar(self, usuario, motivo):
        """Rechaza la matrícula con un motivo visible al representante."""
        if not motivo:
            raise ValidationError('Debe especificar el motivo del rechazo.')
        if self.estado not in [self.ESTADO_EN_REVISION, self.ESTADO_PENDIENTE]:
            raise ValidationError('No se puede rechazar en el estado actual.')
        estado_anterior = self.estado
        self.estado = self.ESTADO_RECHAZADA
        self.fecha_resolucion = timezone.now()
        self.revisado_por = usuario
        self.motivo_rechazo = motivo
        self.numero_intentos += 1
        self.save()
        self._registrar_historial(estado_anterior, self.ESTADO_RECHAZADA, usuario, motivo)

    def anular(self, usuario, motivo):
        """Anula una matrícula aprobada (solo en casos excepcionales)."""
        if self.estado != self.ESTADO_APROBADA:
            raise ValidationError('Solo se pueden anular matrículas aprobadas.')
        if not motivo:
            raise ValidationError('Debe especificar el motivo de anulación.')
        self.estado = self.ESTADO_ANULADA
        self.fecha_anulacion = timezone.now()
        self.anulado_por = usuario
        self.motivo_anulacion = motivo
        self.save()
        self._registrar_historial(self.ESTADO_APROBADA, self.ESTADO_ANULADA, usuario, motivo)

    def reenviar(self, usuario):
        """El representante reenvía la solicitud rechazada con correcciones."""
        if self.estado != self.ESTADO_RECHAZADA:
            raise ValidationError('Solo se puede reenviar una solicitud rechazada.')
        self.estado = self.ESTADO_PENDIENTE
        self.motivo_rechazo = ''
        self.save()
        self._registrar_historial(self.ESTADO_RECHAZADA, self.ESTADO_PENDIENTE, usuario,
                                  'Representante reenvió la solicitud con correcciones.')

    def _registrar_historial(self, estado_anterior, estado_nuevo, usuario, comentario=''):
        HistorialMatricula.objects.create(
            matricula=self,
            estado_anterior=estado_anterior,
            estado_nuevo=estado_nuevo,
            usuario=usuario,
            comentario=comentario,
        )

    # ─── Propiedades útiles ───────────────────────────────────────────────────
    @property
    def es_editable(self):
        return self.estado in self.ESTADOS_EDITABLES

    @property
    def esta_finalizada(self):
        return self.estado in self.ESTADOS_FINALES

    @property
    def dias_en_proceso(self):
        if not self.fecha_solicitud:
            return 0
        if self.fecha_resolucion:
            delta = self.fecha_resolucion - self.fecha_solicitud
        else:
            delta = timezone.now() - self.fecha_solicitud
        return delta.days


class HistorialMatricula(models.Model):
    """
    Registro inmutable de cada cambio de estado en la matrícula.
    Proporciona auditoría completa del proceso.
    """
    matricula       = models.ForeignKey(Matricula, on_delete=models.CASCADE,
                                        related_name='historial')
    estado_anterior = models.CharField(max_length=15, verbose_name='Estado anterior')
    estado_nuevo    = models.CharField(max_length=15, verbose_name='Estado nuevo')
    usuario         = models.ForeignKey(Usuario, on_delete=models.SET_NULL,
                                        null=True, verbose_name='Usuario que realizó el cambio')
    fecha           = models.DateTimeField(auto_now_add=True, verbose_name='Fecha del cambio')
    comentario      = models.TextField(blank=True, verbose_name='Comentario')

    class Meta:
        verbose_name        = 'Historial de matrícula'
        verbose_name_plural = 'Historial de matrículas'
        ordering            = ['-fecha']

    def __str__(self):
        return (f'{self.matricula.codigo}: '
                f'{self.estado_anterior} → {self.estado_nuevo} '
                f'({self.fecha:%Y-%m-%d %H:%M})')